<script setup lang="ts">
import { ref, provide } from 'vue'
import { useLiveReadings } from '@/composables/useLiveReadings'
import NodeStatus from '@/components/NodeStatus.vue'
import SensorCard from '@/components/SensorCard.vue'
import SensorChart from '@/components/SensorChart.vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Leaf } from 'lucide-vue-next'

const NODE_ID = 'tent-1'
const SENSOR_ID = 'canopy'

const liveReadings = useLiveReadings()
provide('liveReadings', liveReadings)

function iso(offsetHours: number): string {
  return new Date(Date.now() - offsetHours * 3_600_000).toISOString()
}

const timeRange = ref({ start: iso(24), stop: new Date().toISOString() })
</script>

<template>
  <div class="min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
    <!-- Header -->
    <header class="border-b border-[hsl(var(--border))] px-6 py-4">
      <div class="mx-auto max-w-7xl flex items-center gap-3">
        <Leaf class="h-6 w-6 text-emerald-500" />
        <h1 class="text-xl font-semibold tracking-tight">AI Botanist</h1>
        <span class="text-[hsl(var(--muted-foreground))] text-sm">/ Dashboard</span>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-6 py-8 flex flex-col gap-8">
      <!-- Node status bar -->
      <section>
        <h2 class="text-xs font-semibold uppercase tracking-widest text-[hsl(var(--muted-foreground))] mb-3">
          Nodes
        </h2>
        <NodeStatus />
      </section>

      <!-- Tent-1 section -->
      <section>
        <h2 class="text-xs font-semibold uppercase tracking-widest text-[hsl(var(--muted-foreground))] mb-4">
          {{ NODE_ID }}
        </h2>

        <!-- Live readings row -->
        <div class="flex flex-wrap gap-4 mb-6">
          <SensorCard :node-id="NODE_ID" :sensor-id="SENSOR_ID" />
          <SensorCard :node-id="NODE_ID" :sensor-id="'floor'" />
        </div>

        <!-- Charts grid -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card v-for="metric in ['temperature', 'humidity', 'co2']" :key="metric">
            <CardHeader class="pb-1">
              <CardTitle class="text-sm capitalize text-[hsl(var(--muted-foreground))]">
                {{ metric }} — last 24 h
              </CardTitle>
            </CardHeader>
            <CardContent class="px-4 pb-4">
              <SensorChart :node-id="NODE_ID" :sensor-id="SENSOR_ID" :metric="metric" :time-range="timeRange" />
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  </div>
</template>
