# frontend — Project Context

## Purpose
Vue 3 + Vite dashboard for the ai-botanist system. Displays live and historical sensor data, camera feed, node status, and an AI agent chat interface. Talks to the FastAPI backend via REST and WebSocket.

---

## Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── SensorCard.vue        # current temp/humidity for one sensor
│   │   ├── SensorChart.vue       # time-series chart (uPlot)
│   │   ├── CameraFeed.vue        # HLS stream via <video> tag
│   │   ├── NodeStatus.vue        # online/offline per node
│   │   └── AgentChat.vue         # AI chat interface
│   ├── views/
│   │   ├── Dashboard.vue         # main overview
│   │   └── Agent.vue             # full-page AI chat
│   ├── composables/
│   │   ├── useLiveReadings.ts    # WebSocket → reactive sensor state
│   │   └── useReadings.ts        # REST queries for historical data
│   └── api/
│       └── index.ts              # typed API client (fetch wrapper)
└── package.json
```

---

## Key Libraries
| Need | Library | Reason |
|---|---|---|
| Charts | uPlot | Lightweight, fast for time-series |
| Camera | Native `<video>` + HLS | go2rtc converts RTSP → HLS |
| WebSocket | Native browser WS | No library needed |
| HTTP | Native fetch | Thin typed wrapper sufficient |

---

## Backend Integration
- Live data: WebSocket at `ws://{host}/ws/live` — pushed on every MQTT publish
- Historical: `GET /readings/{node_id}/{sensor_id}` with time range params
- AI agent: `POST /agent/chat` with message history, streamed response
- Camera: HLS stream from go2rtc at `http://{host}:1984/{stream_name}`

---

## Implementation Checklist
- [ ] Vite + Vue 3 + TypeScript scaffold
- [ ] API client (`api/index.ts`)
- [ ] WebSocket composable (`useLiveReadings.ts`)
- [ ] `SensorCard` — live reading display
- [ ] `SensorChart` — historical chart with uPlot
- [ ] `Dashboard` view — cards + charts per node
- [ ] `CameraFeed` — HLS stream
- [ ] `AgentChat` component + `Agent` view
- [ ] Node status indicators