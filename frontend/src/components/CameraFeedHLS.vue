<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Hls from 'hls.js'

const props = defineProps<{
  nodeId: string
  cameraId: string
}>()

const GO2RTC_URL = (import.meta.env.VITE_GO2RTC_URL as string) ?? 'http://localhost:1984'

const streamName = `${props.nodeId}_${props.cameraId}`
const streamUrl = `${GO2RTC_URL}/api/stream.m3u8?src=${streamName}`

const videoRef = ref<HTMLVideoElement>()
const loading = ref(true)

let hls: Hls | null = null

onMounted(() => {
  if (!videoRef.value) return

  if (Hls.isSupported()) {
    hls = new Hls({ lowLatencyMode: false })
    hls.loadSource(streamUrl)
    hls.attachMedia(videoRef.value)
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      loading.value = false
      videoRef.value?.play().catch(() => {})
    })
  } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
    videoRef.value.src = streamUrl
    videoRef.value.addEventListener('loadedmetadata', () => {
      loading.value = false
      videoRef.value?.play().catch(() => {})
    })
  }
})

onUnmounted(() => {
  hls?.destroy()
  hls = null
})
</script>

<template>
  <div
    class="relative w-full aspect-video bg-[hsl(var(--card))] rounded-lg overflow-hidden border border-[hsl(var(--border))]"
  >
    <video ref="videoRef" class="w-full h-full object-cover" muted playsinline />

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
