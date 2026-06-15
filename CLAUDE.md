# ai-botanist — Project Context

## Goal
Self-hosted IoT grow tent monitoring system with an AI agent layer. Sensor data flows from grow nodes → MQTT → InfluxDB, served via a FastAPI backend and Vue frontend. Designed to scale to multiple tents/nodes.

## Repo Structure
```
ai-botanist/
├── grow-node/   # Pi sensor app (Python)
├── backend/     # FastAPI — data API + AI agent
├── frontend/    # Vue + Vite — dashboard + AI chat
└── infra/       # Docker Compose + service configs
```

## Data Flow
```
[Grow Nodes]  →  Mosquitto  →  Telegraf  →  InfluxDB
                                                 ↑
                                            FastAPI
                                                 ↑
                                         Vue Frontend
```

## MQTT Topic Structure
```
grows/{node_id}/{sensor_id}/temperature
grows/{node_id}/{sensor_id}/humidity
grows/{node_id}/{sensor_id}/co2
grows/{node_id}/camera/snapshot
```

## Stack
| Layer | Tool |
|---|---|
| Node sensors | I2C (SHT31-D), GPIO (DHT22), BLE (TP358), UART |
| Node app | Python, paho-mqtt |
| Broker | Mosquitto |
| Bridge | Telegraf (MQTT → InfluxDB) |
| Database | InfluxDB |
| Camera proxy | go2rtc (RTSP → WebRTC, temp) |
| API | FastAPI (Python) |
| Frontend | Vue 3 + Vite |
| AI agent | Anthropic SDK (Python) |

## Key Decisions
| Decision | Choice | Reason |
|---|---|---|
| Monorepo | Yes | Single CLAUDE.md hierarchy, manageable scale |
| Backend language | Python | Matches node app, native Anthropic SDK |
| Frontend | Vue + Vite | Developer familiarity |
| No Grafana | Custom frontend | Required for AI agent integration |
| Camera | go2rtc → WebRTC (temporary) | HLS dropped: hls.js hammered the same segments hundreds of times per second and never displayed anything. WebRTC works locally but may fail from RPi on tricky networks (needs direct connectivity); HLS remains the longer-term fallback to revisit |