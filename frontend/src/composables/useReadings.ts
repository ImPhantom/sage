import { ref, watch, type Ref } from 'vue'
import { api, type SensorReading } from '@/api'

export interface TimeRange {
  start: string
  stop: string
}

export function useReadings(
  nodeId: string | Ref<string>,
  sensorId: string | Ref<string>,
  metric: string | Ref<string>,
  timeRange: Ref<TimeRange>,
) {
  const data = ref<SensorReading[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetch() {
    const nId = typeof nodeId === 'string' ? nodeId : nodeId.value
    const sId = typeof sensorId === 'string' ? sensorId : sensorId.value
    const m = typeof metric === 'string' ? metric : metric.value

    loading.value = true
    error.value = null
    try {
      data.value = await api.getReadings(nId, sId, m, timeRange.value.start, timeRange.value.stop)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'fetch failed'
    } finally {
      loading.value = false
    }
  }

  watch(timeRange, fetch, { immediate: true, deep: true })

  return { data, loading, error, refresh: fetch }
}
