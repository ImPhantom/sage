<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  nodeId: string
  cameraId: string
}>()

const GO2RTC_URL = (import.meta.env.VITE_GO2RTC_URL as string) ?? 'http://localhost:1984'

const streamName = `${props.nodeId}_${props.cameraId}`
const videoRef = ref<HTMLVideoElement>()
const loading = ref(true)

let pc: RTCPeerConnection | null = null
let retryTimer: ReturnType<typeof setTimeout> | null = null
let stopped = false

function scheduleRetry() {
  if (stopped || retryTimer) return
  retryTimer = setTimeout(() => {
    retryTimer = null
    connect()
  }, 5000)
}

async function connect() {
  if (stopped || !videoRef.value) return

  pc?.close()
  pc = new RTCPeerConnection()

  pc.addTransceiver('video', { direction: 'recvonly' })

  pc.ontrack = (event) => {
    if (videoRef.value && event.streams[0]) {
      videoRef.value.srcObject = event.streams[0]
      videoRef.value.play().catch(() => {})
    }
  }

  pc.onconnectionstatechange = () => {
    if (pc?.connectionState === 'connected') {
      loading.value = false
    } else if (pc?.connectionState === 'failed') {
      // 'disconnected' is transient and may self-recover — only restart on 'failed'
      loading.value = true
      pc?.close()
      pc = null
      scheduleRetry()
    }
  }

  try {
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    // Wait for ICE gathering to finish — go2rtc requires all candidates in the offer
    await new Promise<void>((resolve) => {
      if (pc!.iceGatheringState === 'complete') { resolve(); return }
      const onStateChange = () => {
        if (pc!.iceGatheringState === 'complete') {
          pc!.removeEventListener('icegatheringstatechange', onStateChange)
          resolve()
        }
      }
      pc!.addEventListener('icegatheringstatechange', onStateChange)
    })

    const resp = await fetch(`${GO2RTC_URL}/api/webrtc?src=${streamName}`, {
      method: 'POST',
      body: pc!.localDescription!.sdp,
      headers: { 'Content-Type': 'application/sdp' },
    })

    if (!resp.ok) throw new Error(`${resp.status}`)

    const sdp = await resp.text()
    await pc.setRemoteDescription({ type: 'answer', sdp })
  } catch {
    pc?.close()
    pc = null
    scheduleRetry()
  }
}

onMounted(connect)

onUnmounted(() => {
  stopped = true
  if (retryTimer) clearTimeout(retryTimer)
  pc?.close()
  pc = null
})
</script>

<template>
  <div
    class="relative w-full aspect-video bg-[hsl(var(--card))] rounded-lg overflow-hidden border border-[hsl(var(--border))]"
  >
    <video ref="videoRef" class="w-full h-full object-cover" autoplay muted playsinline />

    <div
      v-if="loading"
      class="absolute inset-0 flex flex-col items-center justify-center gap-2"
    >
      <div
        class="h-6 w-6 rounded-full border-2 border-[hsl(var(--muted-foreground))] border-t-transparent animate-spin"
      />
      <span class="font-mono text-xs opacity-40">{{ streamName }}</span>
    </div>

    <div
      v-if="!loading"
      class="absolute bottom-2 left-2 rounded bg-black/50 px-1.5 py-0.5"
    >
      <span class="font-mono text-[10px] text-white/70">{{ cameraId }}</span>
    </div>
  </div>
</template>
