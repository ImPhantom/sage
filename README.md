# ai-botanist

Self-hosted IoT grow tent monitoring. Sensor nodes publish to MQTT → InfluxDB, served via a FastAPI backend and Vue frontend with an AI agent layer.

## Running the stack

Requires Docker, Bun, and Python with a populated `backend/.venv`.

```sh
bun install
bun run dev
```

This starts the infra (Docker Compose), the FastAPI backend, and the Vite dev server together. `Ctrl+C` stops all three.

## Setting up a grow node (Raspberry Pi)

Sparse-checkout so you only pull the `grow-node/` directory:

```sh
git clone --filter=blob:none --sparse <repo-url> ai-botanist
cd ai-botanist
git sparse-checkout set grow-node
cd grow-node
```

Install dependencies:

```sh
pip install -r requirements-pi.txt
```

Edit `config.yaml` — set your `node_id`, MQTT broker IP, and sensor interfaces, then run:

```sh
python main.py
```

To run on boot, see the systemd service instructions in [`grow-node/README.md`](grow-node/README.md).
