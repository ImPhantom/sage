<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide } from 'vue'
import { useLiveReadings } from '@/composables/useLiveReadings'
import { api, type NodeInfo } from '@/api'
import SensorCard from '@/components/SensorCard.vue'
import SensorChart from '@/components/SensorChart.vue'
import CameraFeed from '@/components/CameraFeed.vue'
import CameraFeedHLS from '@/components/CameraFeedHLS.vue'
import Badge from '@/components/ui/Badge.vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Leaf, Circle } from 'lucide-vue-next'
import type { TimeRange } from '@/composables/useReadings'

const liveReadings = useLiveReadings()
provide('liveReadings', liveReadings)

const nodes = ref<NodeInfo[]>([])
let nodeTimer: ReturnType<typeof setInterval> | null = null

async function loadNodes() {
  try {
    nodes.value = await api.getNodes()
  } catch {
    // keep stale data on error
  }
}

onMounted(() => {
  loadNodes()
  nodeTimer = setInterval(loadNodes, 30_000)
})

onUnmounted(() => {
  if (nodeTimer) clearInterval(nodeTimer)
})

function iso(offsetHours: number): string {
  return new Date(Date.now() - offsetHours * 3_600_000).toISOString()
}

const timeRange = ref<TimeRange>({ start: iso(24), stop: new Date().toISOString() })

const ONLINE_THRESHOLD_MS = 5 * 60 * 1000

function isOnline(node: NodeInfo): boolean {
  if (!node.last_seen) return false
  return Date.now() - new Date(node.last_seen).getTime() < ONLINE_THRESHOLD_MS
}

function lastSeenLabel(node: NodeInfo): string {
  if (!node.last_seen) return 'never'
  const diff = Date.now() - new Date(node.last_seen).getTime()
  const s = Math.floor(diff / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  return `${Math.floor(m / 60)}h ago`
}

function getSensorIds(nodeId: string): string[] {
  return Object.keys(liveReadings.readings[nodeId] ?? {})
}

const METRICS = ['temperature', 'humidity', 'co2'] as const
</script>

<template>
  <div class="min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
    <header class="border-b border-[hsl(var(--border))] px-6 py-4">
      <div class="mx-auto max-w-7xl flex items-center gap-3">
        <Leaf class="h-6 w-6 text-emerald-500" />
        <h1 class="text-xl font-semibold tracking-tight">AI Botanist</h1>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-6 py-8 flex flex-col gap-10">
      <section v-for="node in nodes" :key="node.node_id">
        <!-- Node header with inline status -->
        <div class="flex items-center gap-3 mb-5">
          <Circle :class="['h-2.5 w-2.5 fill-current', isOnline(node) ? 'text-emerald-500' : 'text-red-500']" />
          <h2 class="text-sm font-semibold uppercase tracking-widest">{{ node.node_id }}</h2>
          <Badge :variant="isOnline(node) ? 'success' : 'destructive'" class="text-[10px] py-0">
            {{ isOnline(node) ? 'online' : 'offline' }}
          </Badge>
          <span class="text-xs text-[hsl(var(--muted-foreground))]">{{ lastSeenLabel(node) }}</span>
        </div>

        <!-- Camera feeds -->
        <div v-if="node.cameras.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-5">
          <CameraFeed v-for="cam in node.cameras" :key="cam.id" :node-id="node.node_id" :camera-id="cam.id" />
        </div>

        <!-- Live sensor readings -->
        <div v-if="getSensorIds(node.node_id).length" class="flex flex-wrap gap-4 mb-5">
          <SensorCard v-for="sId in getSensorIds(node.node_id)" :key="sId" :node-id="node.node_id" :sensor-id="sId" />
        </div>

        <!-- Historical charts — one per metric, all sensors on each -->
        <div v-if="getSensorIds(node.node_id).length" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card v-for="metric in METRICS" :key="metric">
            <CardHeader class="pb-1">
              <CardTitle class="text-sm capitalize text-[hsl(var(--muted-foreground))]">
                {{ metric }}
              </CardTitle>
            </CardHeader>
            <CardContent class="px-4 pb-4">
              <SensorChart :node-id="node.node_id" :sensor-ids="getSensorIds(node.node_id)" :metric="metric" :time-range="timeRange" />
            </CardContent>
          </Card>
        </div>
      </section>

      <div v-if="nodes.length === 0" class="text-sm text-[hsl(var(--muted-foreground))]">
        No nodes registered yet.
      </div>
    </main>
  </div>
</template>
