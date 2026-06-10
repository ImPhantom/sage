# infra

Docker Compose stack for the ai-botanist backend host. Runs Mosquitto, InfluxDB, Telegraf, and go2rtc.

## Prerequisites

- Docker with the Compose plugin (`docker compose version`)
- `mosquitto-clients` on the host for smoke-testing (`apt install mosquitto-clients` or `brew install mosquitto`)

## First-time setup

```bash
cp .env.example .env
```

Edit `.env` — set a strong `INFLUXDB_ADMIN_PASSWORD` and generate a random `INFLUXDB_TOKEN`:

```bash
# Quick token generator (Linux/Mac)
openssl rand -hex 32
```

## Bring up the stack

```bash
docker compose up -d
```

InfluxDB runs first-time setup automatically using the values in `.env`. Telegraf starts subscribing to Mosquitto once both are up.

## Verify data is flowing

### 1. Publish a test message

```bash
mosquitto_pub -h localhost -p 1883 \
  -t "grows/node1/sensor1/temperature" \
  -m "22.5"
```

### 2. Query InfluxDB for the ingested point

Open `http://localhost:8086` and log in with `INFLUXDB_ADMIN_USER` / `INFLUXDB_ADMIN_PASSWORD`.

In the **Data Explorer**, run this Flux query:

```flux
from(bucket: "grow-tent")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "temperature")
```

You should see one row with:
- `node_id = "node1"`
- `sensor_id = "sensor1"`
- `_value = 22.5`

Telegraf flushes every 10 seconds, so wait a moment after publishing before querying.

## Stopping

```bash
# Stop containers, keep volumes
docker compose down

# Stop and wipe all data (fresh start)
docker compose down -v
```

## Notes

- Mosquitto listens on port `1883`, no authentication (local network only).
- InfluxDB UI is at `http://localhost:8086`.
- go2rtc streams are configured in `go2rtc/go2rtc.yaml` (stub for now).
- The grow-node app runs directly on each Pi — it is **not** part of this Compose stack.
