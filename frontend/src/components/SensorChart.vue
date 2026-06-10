<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import uPlot from 'uplot'
import 'uplot/dist/uPlot.min.css'
import { useReadings, type TimeRange } from '@/composables/useReadings'

const props = defineProps<{
  nodeId: string
  sensorId: string
  metric: string
  timeRange: TimeRange
}>()

const containerRef = ref<HTMLDivElement>()
let chart: uPlot | null = null

const timeRangeRef = computed(() => props.timeRange)
const { data } = useReadings(
  computed(() => props.nodeId),
  computed(() => props.sensorId),
  computed(() => props.metric),
  timeRangeRef,
)

const METRIC_COLOR: Record<string, string> = {
  temperature: '#fb923c',
  humidity: '#38bdf8',
  co2: '#4ade80',
}

function buildOpts(width: number): uPlot.Options {
  const color = METRIC_COLOR[props.metric] ?? '#a78bfa'
  return {
    width,
    height: 180,
    class: 'uplot-dark',
    scales: { x: { time: true } },
    axes: [
      {
        stroke: '#6b7280',
        grid: { stroke: '#1f2937', width: 1 },
        ticks: { stroke: '#374151' },
      },
      {
        stroke: '#6b7280',
        grid: { stroke: '#1f2937', width: 1 },
        ticks: { stroke: '#374151' },
        size: 50,
      },
    ],
    series: [
      {},
      {
        label: props.metric,
        stroke: color,
        width: 2,
        fill: `${color}22`,
      },
    ],
    cursor: { show: false },
    legend: { show: false },
  }
}

function buildData(): uPlot.AlignedData {
  const xs = data.value.map((r) => Math.floor(new Date(r.time).getTime() / 1000))
  const ys = data.value.map((r) => r.value)
  return [xs, ys]
}

function initChart() {
  if (!containerRef.value) return
  const width = containerRef.value.clientWidth || 400
  chart = new uPlot(buildOpts(width), buildData(), containerRef.value)
}

function updateChart() {
  if (!chart) return
  chart.setData(buildData())
}

watch(data, () => {
  if (chart) updateChart()
  else initChart()
})

let ro: ResizeObserver | null = null

onMounted(() => {
  initChart()
  if (containerRef.value) {
    ro = new ResizeObserver((entries) => {
      const w = entries[0].contentRect.width
      chart?.setSize({ width: w, height: 180 })
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
    <div class="mb-1 text-xs font-medium uppercase tracking-wider text-[hsl(var(--muted-foreground))]">
      {{ metric }}
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
