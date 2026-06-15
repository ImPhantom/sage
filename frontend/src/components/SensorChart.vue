<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import uPlot from 'uplot'
import 'uplot/dist/uPlot.min.css'
import { api, type SensorReading } from '@/api'
import type { TimeRange } from '@/composables/useReadings'

const props = defineProps<{
  nodeId: string
  sensorIds: string[]
  metric: string
  timeRange: TimeRange
}>()

const containerRef = ref<HTMLDivElement>()
let chart: uPlot | null = null

const PALETTE = ['#fb923c', '#38bdf8', '#4ade80', '#c084fc', '#f472b6', '#facc15']

const allData = ref<Record<string, SensorReading[]>>({})

async function fetchAll() {
  if (!props.sensorIds.length) return
  const results = await Promise.allSettled(
    props.sensorIds.map((sId) =>
      api
        .getReadings(props.nodeId, sId, props.metric, props.timeRange.start, props.timeRange.stop)
        .then((data) => ({ sId, data })),
    ),
  )
  const next: Record<string, SensorReading[]> = {}
  for (const r of results) {
    if (r.status === 'fulfilled') next[r.value.sId] = r.value.data
  }
  allData.value = next
}

function buildOpts(width: number): uPlot.Options {
  const sensorSeries: uPlot.Series[] = props.sensorIds.map((sId, i) => ({
    label: sId,
    stroke: PALETTE[i % PALETTE.length],
    width: 2,
    fill: `${PALETTE[i % PALETTE.length]}18`,
  }))

  return {
    width,
    height: 160,
    class: 'uplot-dark',
    scales: { x: { time: true } },
    axes: [
      { stroke: '#6b7280', grid: { stroke: '#1f2937', width: 1 }, ticks: { stroke: '#374151' } },
      {
        stroke: '#6b7280',
        grid: { stroke: '#1f2937', width: 1 },
        ticks: { stroke: '#374151' },
        size: 50,
      },
    ],
    series: [{}, ...sensorSeries],
    cursor: { show: false },
    legend: { show: false },
  }
}

function buildData(): uPlot.AlignedData {
  const tsSet = new Set<number>()
  const maps: Map<number, number>[] = props.sensorIds.map((sId) => {
    const m = new Map<number, number>()
    for (const r of allData.value[sId] ?? []) {
      const ts = Math.floor(new Date(r.time).getTime() / 1000)
      tsSet.add(ts)
      m.set(ts, r.value)
    }
    return m
  })

  const xs = Array.from(tsSet).sort((a, b) => a - b)
  const series = maps.map((m) => xs.map((ts) => m.get(ts) ?? null)) as (number | null)[][]
  return [xs, ...series]
}

function initChart() {
  chart?.destroy()
  chart = null
  if (!containerRef.value || !props.sensorIds.length) return
  const width = containerRef.value.clientWidth || 400
  chart = new uPlot(buildOpts(width), buildData(), containerRef.value)
}

watch(allData, () => {
  if (chart) chart.setData(buildData())
  else initChart()
})

// Re-init when the sensor list actually changes (ignore reference-only changes)
watch(
  () => [...props.sensorIds].sort().join(','),
  () => {
    fetchAll()
    initChart()
  },
)

watch(() => props.timeRange, fetchAll, { deep: true })

let ro: ResizeObserver | null = null

onMounted(() => {
  fetchAll()
  if (containerRef.value) {
    ro = new ResizeObserver((entries) => {
      const w = entries[0].contentRect.width
      chart?.setSize({ width: w, height: 160 })
    })
    ro.observe(containerRef.value)
  }
})

onUnmounted(() => {
  ro?.disconnect()
  chart?.destroy()
  chart = null
})
</script>

<template>
  <div class="w-full">
    <div v-if="sensorIds.length > 1" class="flex flex-wrap gap-3 mb-2">
      <div v-for="(sId, i) in sensorIds" :key="sId" class="flex items-center gap-1.5">
        <span
          class="inline-block h-2 w-4 rounded-full"
          :style="{ background: PALETTE[i % PALETTE.length] }"
        />
        <span class="text-xs text-[hsl(var(--muted-foreground))]">{{ sId }}</span>
      </div>
    </div>
    <div ref="containerRef" class="w-full" />
  </div>
</template>

<style>
.uplot-dark .u-wrap {
  background: transparent;
}
.uplot-dark canvas {
  border-radius: 0.5rem;
}
</style>
