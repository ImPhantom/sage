# ai-botanist backend

FastAPI service that queries InfluxDB for sensor data and exposes it to the frontend.

## Prerequisites

- Python 3.11+
- InfluxDB running (start with `cd infra && docker compose up -d`)

## Setup

```bash
cd backend
cp .env.example .env
# edit .env — copy INFLUXDB_TOKEN from infra/.env
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Endpoints

### Health check
```bash
curl http://localhost:8000/health
```

### Latest reading per sensor across all nodes
```bash
curl http://localhost:8000/readings/latest
```

### Sensor history — last hour (default)
```bash
curl "http://localhost:8000/readings/tent-1/sensor-1/temperature"
```

### Sensor history — custom range (Flux relative duration)
```bash
curl "http://localhost:8000/readings/tent-1/sensor-1/humidity?start=-6h"
```

### Sensor history — absolute time range (RFC3339)
```bash
curl "http://localhost:8000/readings/tent-1/sensor-1/co2?start=2026-05-24T00:00:00Z&stop=2026-05-24T12:00:00Z"
```

### All nodes with last-seen timestamp
```bash
curl http://localhost:8000/nodes
```
