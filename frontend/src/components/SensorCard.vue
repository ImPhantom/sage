<script setup lang="ts">
import { computed, inject } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Thermometer, Droplets } from 'lucide-vue-next'
import type { useLiveReadings } from '@/composables/useLiveReadings'

const props = defineProps<{
  nodeId: string
  sensorId: string
}>()

const { getReading } = inject<ReturnType<typeof useLiveReadings>>('liveReadings')!

const temp = computed(() => getReading(props.nodeId, props.sensorId, 'temperature'))
const humidity = computed(() => getReading(props.nodeId, props.sensorId, 'humidity'))

function fmt(val: number | undefined, decimals = 1): string {
  return val === undefined ? '—' : val.toFixed(decimals)
}
</script>

<template>
  <Card class="min-w-[200px]">
    <CardHeader class="pb-2">
      <CardTitle class="text-sm text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
        {{ sensorId }}
      </CardTitle>
    </CardHeader>
    <CardContent class="flex flex-col gap-3">
      <div class="flex items-center gap-2">
        <Thermometer class="h-5 w-5 text-orange-400 shrink-0" />
        <span class="text-2xl font-bold tabular-nums text-[hsl(var(--foreground))]">
          {{ fmt(temp?.value) }}<span class="text-sm font-normal text-[hsl(var(--muted-foreground))]">°C</span>
        </span>
      </div>
      <div class="flex items-center gap-2">
        <Droplets class="h-5 w-5 text-sky-400 shrink-0" />
        <span class="text-2xl font-bold tabular-nums text-[hsl(var(--foreground))]">
          {{ fmt(humidity?.value) }}<span class="text-sm font-normal text-[hsl(var(--muted-foreground))]">%</span>
        </span>
      </div>
    </CardContent>
  </Card>
</template>
