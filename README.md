# 🌿Sage 

Self-hosted IoT grow tent monitoring. Sensor nodes publish to MQTT → InfluxDB, served via a FastAPI backend and Vue frontend with an AI agent layer.

## Running the stack

Requires Docker, Bun, and Python with a populated `backend/.venv`.

```sh
bun install
bun run dev
```

This starts the infra (Docker Compose), the FastAPI backend, and the Vite dev server together. `Ctrl+C` stops all three.

## Setting up a grow node (Raspberry Pi)

See [`grow-node/README.md`](grow-node/README.md).
