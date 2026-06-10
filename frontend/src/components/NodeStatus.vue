<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { api, type NodeInfo } from '@/api'
import Badge from '@/components/ui/Badge.vue'
import { Circle } from 'lucide-vue-next'

const nodes = ref<NodeInfo[]>([])
let pollTimer: ReturnType<typeof setInterval> | null = null

async function load() {
  try {
    nodes.value = await api.getNodes()
  } catch {
    // keep stale data on error
  }
}

onMounted(() => {
  load()
  pollTimer = setInterval(load, 30_000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

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
</script>

<template>
  <div class="flex flex-wrap gap-3">
    <div
      v-for="node in nodes"
      :key="node.node_id"
      class="flex items-center gap-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-3 py-2"
    >
      <Circle
        :class="['h-2.5 w-2.5 fill-current', isOnline(node) ? 'text-emerald-500' : 'text-red-500']"
      />
      <span class="text-sm font-medium text-[hsl(var(--foreground))]">{{ node.node_id }}</span>
      <Badge :variant="isOnline(node) ? 'success' : 'destructive'" class="text-[10px] py-0">
        {{ isOnline(node) ? 'online' : 'offline' }}
      </Badge>
      <span class="text-xs text-[hsl(var(--muted-foreground))]">{{ lastSeenLabel(node) }}</span>
    </div>
    <div
      v-if="nodes.length === 0"
      class="text-sm text-[hsl(var(--muted-foreground))]"
    >
      Loading nodes…
    </div>
  </div>
</template>
