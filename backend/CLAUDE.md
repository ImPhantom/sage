# backend — Project Context

## Purpose
FastAPI app serving as the central hub — queries InfluxDB for sensor history, exposes live data via WebSocket, and hosts the AI agent. Runs in Docker on the backend host alongside Mosquitto, Telegraf, and InfluxDB.

---

## Structure
```
backend/
├── main.py
├── routers/
│   ├── readings.py     # REST endpoints for sensor data
│   ├── agent.py        # AI agent chat endpoint
│   └── nodes.py        # node status/metadata
├── services/
│   ├── influx.py       # InfluxDB query helpers
│   ├── mqtt.py         # MQTT subscriber (live data, node status)
│   └── agent.py        # Anthropic SDK + tool definitions
└── requirements.txt
```

---

## API Surface
```
GET  /readings/{node_id}/{sensor_id}   # historical data from InfluxDB
GET  /readings/latest                  # latest reading per sensor across all nodes
WS   /ws/live                          # live sensor readings pushed from MQTT
POST /agent/chat                       # AI agent — question about the grow
GET  /nodes                            # registered nodes and last-seen status
```

---

## AI Agent
The agent answers questions grounded in real grow data via tools:

| Tool | Description |
|---|---|
| `query_readings` | Query InfluxDB for a sensor's history over a time range |
| `get_latest` | Get current readings across all sensors |
| `get_node_status` | Check which nodes are online |

Agent lives in `services/agent.py`. Uses the Anthropic SDK. Routed via `routers/agent.py`.

---

## Key Decisions
| Decision | Choice | Reason |
|---|---|---|
| Framework | FastAPI | Async-native, WebSocket support, clean with paho-mqtt |
| Live data | WebSocket | Push from MQTT subscriber to frontend without polling |
| AI SDK | Anthropic Python SDK | Tool use, grounded responses from InfluxDB |
| No Grafana | Custom only | Grafana can't host an AI agent interface |

---

## Implementation Checklist
- [x] FastAPI skeleton with `/health`
- [x] InfluxDB client + query helpers (`services/influx.py`)
- [x] `/readings` endpoints
- [x] Node status tracking (`GET /nodes`)
- [x] MQTT subscriber → WebSocket bridge (`WS /ws/live`)
- [ ] AI agent scaffold with tool definitions (`services/agent.py`)
- [x] `/agent/chat` endpoint (stub — returns hardcoded response)
- [ ] Dockerized with `docker-compose.yml` in `infra/`