# infra — Project Context

## Purpose
Docker Compose stack for the backend host. Runs all services except the grow-node app (which runs directly on each Pi).

---

## Services
```
infra/
├── docker-compose.yml
├── mosquitto/
│   └── mosquitto.conf      # listener 1883, allow anonymous
├── telegraf/
│   └── telegraf.conf       # MQTT consumer → InfluxDB output
└── go2rtc/
    └── go2rtc.yaml         # RTSP stream → HLS
```

## Service Map
| Service | Port | Purpose |
|---|---|---|
| Mosquitto | 1883 | MQTT broker — receives all node publishes |
| Telegraf | — | Subscribes to `grows/#`, writes to InfluxDB |
| InfluxDB | 8086 | Time-series storage |
| go2rtc | 1984 | RTSP → HLS proxy for camera feeds |
| backend | 8000 | FastAPI app |
| frontend | 80 | nginx serving Vite build |

## Telegraf MQTT → InfluxDB Mapping
- Subscribes to `grows/#`
- Topic parsed to extract `node_id` and `sensor_id` as tags
- Measurement name derived from the final topic segment (e.g. `temperature`)

---

## Implementation Checklist
- [x] `docker-compose.yml` with all services
- [x] `mosquitto.conf` — basic listener, no auth (local network only)
- [x] `telegraf.conf` — MQTT consumer + InfluxDB output + topic tag parsing
- [x] `go2rtc.yaml` — no static streams; streams registered at runtime via backend → go2rtc HTTP API
- [ ] Confirm data flows: node → Mosquitto → Telegraf → InfluxDB
- [x] Add backend + frontend services to Compose