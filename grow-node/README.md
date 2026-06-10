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
├── config.yaml          # sensor and MQTT configuration
├── config.py            # loads and validates config.yaml
├── drivers/
│   ├── __init__.py      # driver registry (interface → class)
│   ├── base.py          # BaseSensor ABC
│   ├── gpio_dht22.py    # DHT22 via adafruit-circuitpython-dht
│   └── simulated.py     # randomised stub for dev/testing
├── publisher.py         # poll loop + MQTT publish
├── main.py              # entry point
├── requirements.txt     # paho-mqtt, PyYAML
└── requirements-pi.txt  # + adafruit-circuitpython-dht, RPi.GPIO
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

```sh
pip install -r requirements-pi.txt
```

The GPIO user must be in the `gpio` group:

```sh
sudo usermod -aG gpio $USER
```

Set sensors back to `interface: gpio` in `config.yaml`, then run `python main.py`. To run on boot with systemd, see [Systemd Service](#systemd-service).

## Configuration Reference

`config.yaml` fields:

| Field | Required | Default | Description |
|---|---|---|---|
| `node_id` | yes | — | Unique node name; used in MQTT topic prefix |
| `poll_interval` | no | `30` | Seconds between sensor reads |
| `mqtt.broker` | yes | — | Broker hostname or IP |
| `mqtt.port` | no | `1883` | Broker port |
| `mqtt.client_id` | no | `node_id` | MQTT client identifier |
| `sensors[].id` | yes | — | Unique sensor name; used in MQTT topic |
| `sensors[].type` | yes | — | Sensor model (e.g. `dht22`, `simulated`) |
| `sensors[].interface` | yes | — | Driver to use — see table below |
| `sensors[].params` | no | `{}` | Driver-specific parameters |

### Sensor Interfaces

| `interface` | Driver | `params` keys |
|---|---|---|
| `gpio` | `GpioDht22Sensor` | `pin` (required), `retries` (default 3), `retry_delay` (default 0.5s) |
| `simulated` | `SimulatedSensor` | `temp_min/max` (default 20–30), `humidity_min/max` (default 40–80) |

Example with all params explicit:

```yaml
sensors:
  - id: canopy
    type: dht22
    interface: gpio
    params:
      pin: 17
      retries: 5
      retry_delay: 0.3

  - id: sim-ambient
    type: simulated
    interface: simulated
    params:
      temp_min: 22.0
      temp_max: 28.0
      humidity_min: 50.0
      humidity_max: 70.0
```

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
