const BASE_URL = (import.meta.env.VITE_API_URL as string) ?? 'http://localhost:8000'

export interface SensorReading {
  time: string
  value: number
}

export interface LatestReading {
  node_id: string
  sensor_id: string
  metric: string
  value: number
  time: string
}

export interface NodeInfo {
  node_id: string
  last_seen: string | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${path}`)
  return res.json() as Promise<T>
}

export const api = {
  getLatestReadings(): Promise<LatestReading[]> {
    return request('/readings/latest')
  },

  getReadings(
    nodeId: string,
    sensorId: string,
    metric: string,
    start: string,
    stop: string,
  ): Promise<SensorReading[]> {
    const params = new URLSearchParams({ start, stop })
    return request(`/readings/${nodeId}/${sensorId}/${metric}?${params}`)
  },

  getNodes(): Promise<NodeInfo[]> {
    return request('/nodes')
  },

  wsUrl(): string {
    const base = BASE_URL.replace(/^http/, 'ws')
    return `${base}/ws/live`
  },
}
