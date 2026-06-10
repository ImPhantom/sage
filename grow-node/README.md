# grow-node

Raspberry Pi sensor node for grow tent monitoring. Reads sensors, publishes readings to MQTT. Part of a larger stack: Mosquitto → InfluxDB → Grafana.

Each node runs independently — it keeps publishing if the backend is unreachable.

## Stack

```
[grow-node]  (Pi 3B+ + sensors)
      |
      | MQTT  grows/{node_id}/{sensor_id}/{metric}
      ↓
[Mosquitto] → [InfluxDB] → [Grafana]
```

## File Structure

```
grow-node/
├── config.yaml          # sensor, camera, and MQTT configuration
├── config.py            # loads and validates config.yaml
├── camera_manager.py    # generates mediamtx config and manages the subprocess
├── drivers/
│   ├── __init__.py      # driver registry (interface → class)
│   ├── base.py          # BaseSensor ABC
│   ├── ble_tp358.py     # ThermoPro TP358 via BLE passive scan
│   ├── gpio_dht22.py    # DHT22 via adafruit-circuitpython-dht
│   ├── i2c_sht31.py     # SHT31-D via I2C
│   └── simulated.py     # randomised stub for dev/testing
├── publisher.py         # poll loop + MQTT publish
├── main.py              # entry point
├── requirements.txt     # paho-mqtt, PyYAML
└── requirements-pi.txt  # + adafruit libs, bleak, RPi.GPIO
```

## Quick Start (dev machine, no hardware)

```sh
pip install -r requirements.txt
```

Edit `config.yaml` and set all sensors to `interface: simulated`. Then run:

```sh
python main.py
```

Logs go to stdout. To see MQTT traffic, start a local broker and subscribe:

```sh
docker run -p 1883:1883 eclipse-mosquitto
mosquitto_sub -t "grows/#" -v
```

Expected output:
```
2026-01-01T12:00:00 INFO     main: Node 'tent-1' — 3 sensor(s), broker=192.168.1.100:1883, interval=30s
2026-01-01T12:00:00 INFO     publisher: Initialized SimulatedSensor(id='canopy')
2026-01-01T12:00:00 INFO     publisher: [canopy] {'temperature': 24.3, 'humidity': 61.2}
```

## Raspberry Pi Setup

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

The GPIO user must be in the `gpio` group:

```sh
sudo usermod -aG gpio $USER
```

Edit `config.yaml`, then run `python main.py`. To run on boot with systemd, see [Systemd Service](#systemd-service).

## Camera Streaming (mediamtx)

Camera support is optional. If no `cameras:` block is present in `config.yaml`, mediamtx is never spawned. If you do declare cameras, `mediamtx` must be on `PATH` before starting the node.

**Linux (Raspberry Pi)**

Find the latest release at https://github.com/bluenviron/mediamtx/releases and pick the right archive for your OS image:

| DietPi image | Archive suffix |
|---|---|
| 64-bit (arm64) | `linux_arm64v8.tar.gz` |
| 32-bit (armv7) | `linux_armv7.tar.gz` |

```sh
VERSION=1.12.3   # replace with the latest release
ARCH=linux_armv7 # or linux_arm64v8
wget https://github.com/bluenviron/mediamtx/releases/download/v${VERSION}/mediamtx_v${VERSION}_${ARCH}.tar.gz
tar xf mediamtx_v${VERSION}_${ARCH}.tar.gz mediamtx
sudo mv mediamtx /usr/local/bin/
```

**Windows (dev)**

Download `mediamtx_vX.Y.Z_windows_amd64.zip` from the releases page, extract `mediamtx.exe`, and add its location to your `PATH`.

## Configuration Reference

See [CONFIG.md](CONFIG.md) for all fields, sensor interfaces, camera types, and a full example.

## MQTT Topics

Each metric is published to its own topic:

```
grows/{node_id}/{sensor_id}/temperature
grows/{node_id}/{sensor_id}/humidity
grows/{node_id}/{sensor_id}/co2
```

Example with `node_id: tent-1` and sensors `canopy`, `floor`:

```
grows/tent-1/canopy/temperature   24.3
grows/tent-1/canopy/humidity      61.2
grows/tent-1/floor/temperature    23.8
grows/tent-1/floor/humidity       58.9
```

Payload is a plain float string. QoS 1, retain=False.

## Adding a Driver

1. Create `drivers/{name}.py` with a class extending `BaseSensor`:

```python
from .base import BaseSensor, SensorReading
from config import SensorConfig

class MyNewSensor(BaseSensor):
    def __init__(self, config: SensorConfig) -> None:
        super().__init__(config)
        # extract from config.params

    def read(self) -> SensorReading:
        # return {"temperature": x} or {"co2": y}, etc.
        ...
```

2. Register it in `drivers/__init__.py`:

```python
try:
    from .my_new_driver import MyNewSensor
    REGISTRY["my-interface"] = MyNewSensor
except (ImportError, RuntimeError):
    pass
```

3. Add any new dependency to `requirements.txt` (or `requirements-pi.txt` if Pi-only).

4. Add a sensor entry to `config.yaml` with `interface: my-interface`.

No other files need to change.

## Systemd Service

Create `/etc/systemd/system/grow-node.service`:

```ini
[Unit]
Description=Grow Node Sensor Publisher
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/grow-node
ExecStart=/home/pi/grow-node/venv/bin/python main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```sh
sudo systemctl enable --now grow-node
journalctl -u grow-node -f
```
