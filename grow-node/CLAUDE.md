# grow-node — Project Context

## Purpose
A self-contained Python app that runs on a Raspberry Pi 3B+ (DietPi headless). Reads sensors and publishes readings to an MQTT broker on the local network. Continues operating independently if the broker or backend goes down.

---

## Sensor Interface Agnostic Design
Sensors are declared in `config.yaml`. The app loads the appropriate driver at runtime based on `interface` type — no sensor logic lives outside of `drivers/`. Adding a new sensor type means adding a new driver file and registering it; nothing else changes.

### Supported Interfaces
| Interface | Example Hardware | Library |
|---|---|---|
| I2C | SHT31-D temp/humidity | `adafruit-circuitpython-sht31d` |
| GPIO | DHT22/AM2302 | `adafruit-circuitpython-dht` |
| Bluetooth (BLE) | ThermoPro TP358 | `bleak` |
| UART/Serial | MH-Z19B CO2 (planned) | `pyserial` |
| USB | Generic USB sensors | `pyserial` or HID |
| Simulated | Dev/testing stub | built-in |

### BLE Note — ThermoPro TP358
The TP358 advertises readings passively via BLE broadcast. It does **not** require a GATT connection. The BLE driver should use `bleak` in **passive scan mode**, filtering by MAC address, and decode the manufacturer data from the advertisement payload. Do not attempt to connect to the device.

---

## Config Format (`config.yaml`)
```yaml
node_id: tent-1
poll_interval: 30
mqtt:
  broker: 192.168.1.x
  port: 1883

sensors:
  - id: canopy
    type: sht31d
    interface: i2c
    params:
      address: 0x44
  - id: floor
    type: sht31d
    interface: i2c
    params:
      address: 0x45
  - id: co2
    type: mhz19b
    interface: uart
    params:
      port: /dev/ttyS0    # future
```

Driver-specific settings go under `params:` — passed to the driver constructor unchanged.

---

## MQTT Topics
```
grows/{node_id}/{sensor_id}/temperature
grows/{node_id}/{sensor_id}/humidity
grows/{node_id}/{sensor_id}/co2
grows/{node_id}/camera/snapshot
```

---

## Current Hardware
- Raspberry Pi 3B+ — DietPi headless
- SHT31-D × 2 wired via I2C (canopy @ 0x44, floor @ 0x45)
- RTSP camera
- DHT22 wiring on hand (22AWG 3-conductor, female dupont 3-pin) for future GPIO sensors

## Planned Sensors
- MH-Z19B CO2 via UART (5V)

---

## Implementation Checklist
- [x] Barebones app scaffolded
- [x] Config loading and validation (`config.py`)
- [x] paho-mqtt publish loop with reconnect handling (`publisher.py`)
- [x] Driver registry pattern (`drivers/__init__.py`)
- [x] Simulated driver with configurable temp/humidity ranges (`drivers/simulated.py`)
- [x] GPIO DHT22 driver with retry logic (`drivers/gpio_dht22.py`) — untested, no hardware available
- [x] BLE driver for ThermoPro TP358 (passive scan, decode advertisement payload)
- [x] Register BLE driver in `drivers/__init__.py`
- [x] I2C SHT31-D driver (`drivers/i2c_sht31.py`) — 0x44/0x45 addresses
- [ ] UART MH-Z19B CO2 driver
- [ ] Multi-node test with second Pi