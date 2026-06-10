import { reactive, onMounted, onUnmounted } from 'vue'
import { api } from '@/api'

export interface LiveReading {
  value: number
  timestamp: string
}

type ReadingMap = Record<string, Record<string, Record<string, LiveReading>>>

interface WsMessage {
  node_id: string
  sensor_id: string
  metric: string
  value: number
  timestamp: string
}

export function useLiveReadings() {
  const readings = reactive<ReadingMap>({})

  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let stopped = false

  function connect() {
    ws = new WebSocket(api.wsUrl())

    ws.onmessage = (evt: MessageEvent) => {
      const msg = JSON.parse(evt.data as string) as WsMessage
      const { node_id, sensor_id, metric, value, timestamp } = msg
      if (!readings[node_id]) readings[node_id] = {}
      if (!readings[node_id][sensor_id]) readings[node_id][sensor_id] = {}
      readings[node_id][sensor_id][metric] = { value, timestamp }
    }

    ws.onclose = () => {
      if (!stopped) {
        reconnectTimer = setTimeout(connect, 3000)
      }
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  async function seed() {
    try {
      const latest = await api.getLatestReadings()
      for (const r of latest) {
        if (!readings[r.node_id]) readings[r.node_id] = {}
        if (!readings[r.node_id][r.sensor_id]) readings[r.node_id][r.sensor_id] = {}
        readings[r.node_id][r.sensor_id][r.metric] = { value: r.value, timestamp: r.time }
      }
    } catch {
      // non-fatal — WebSocket will populate on next push
    }
  }

  onMounted(() => {
    stopped = false
    seed()
    connect()
  })

  onUnmounted(() => {
    stopped = true
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws?.close()
  })

  function getReading(nodeId: string, sensorId: string, metric: string): LiveReading | undefined {
    return readings[nodeId]?.[sensorId]?.[metric]
  }

  return { readings, getReading }
}
