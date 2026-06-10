# grow-node configuration

All configuration lives in `config.yaml` in the `grow-node/` directory. Copy `config.yaml` and edit it before running `python main.py`.

---

## Top-level fields

```yaml
node_id: tent-1        # required — unique name for this node, used in MQTT topics
poll_interval: 30      # optional — seconds between sensor reads, default 30
```

`node_id` must be unique across all nodes publishing to the same broker. It becomes the first segment of every MQTT topic: `grows/{node_id}/...`

---

## `mqtt`

```yaml
mqtt:
  broker: 192.168.1.10   # required — IP or hostname of the MQTT broker
  port: 1883             # optional — default 1883
  client_id: tent-1-node # optional — defaults to node_id if omitted
```

---

## `sensors`

A required, non-empty list. Each sensor needs an `id`, `type`, and `interface`. Sensor IDs must be unique within the node.

```yaml
sensors:
  - id: canopy           # unique name for this sensor, used in MQTT topics
    type: sht31d         # human label — not parsed by the app
    interface: i2c       # selects the driver
    params:              # driver-specific settings (see below)
      address: 0x44
```

The `type` field is a free-form label (used only in logs) — it has no effect on which driver is loaded. The `interface` field selects the driver.

### I2C — SHT31-D (temp + humidity)

Two SHT31-D sensors can be wired on the same I2C bus using different addresses.

```yaml
- id: canopy
  type: sht31d
  interface: i2c
  params:
    address: 0x44   # required — 0x44 or 0x45
```

| param | required | description |
|---|---|---|
| `address` | yes | I2C address — `0x44` (ADDR pin low) or `0x45` (ADDR pin high) |

Publishes: `temperature`, `humidity`

### GPIO — DHT22 / AM2302 (temp + humidity)

```yaml
- id: floor
  type: dht22
  interface: gpio
  params:
    pin: 17          # required — BCM GPIO pin number
    retries: 3       # optional — read attempts before failing, default 3
    retry_delay: 0.5 # optional — seconds between retries, default 0.5
```

| param | required | description |
|---|---|---|
| `pin` | yes | BCM GPIO pin number. Supported: `4, 17, 18, 22, 23, 24, 25, 27` |
| `retries` | no | Read attempts before raising an error. Default `3` |
| `retry_delay` | no | Seconds to wait between retries. Default `0.5` |

Publishes: `temperature`, `humidity`

### Bluetooth — ThermoPro TP358 (temp + humidity)

The TP358 broadcasts readings passively via BLE advertisement — no pairing needed. Find the MAC address in the ThermoPro app or by scanning with `bluetoothctl`.

```yaml
- id: ambient
  type: tp358
  interface: bluetooth
  params:
    mac: "A4:C1:38:XX:XX:XX"  # required — device MAC address
    scan_timeout: 10.0         # optional — seconds to wait for an advertisement, default 10.0
```

| param | required | description |
|---|---|---|
| `mac` | yes | BLE MAC address of the TP358 (case-insensitive) |
| `scan_timeout` | no | How long to listen for an advertisement before failing. Default `10.0` |

Publishes: `temperature`, `humidity`

### Simulated (development / testing)

Generates random values within a configured range. Useful for testing the pipeline without hardware.

```yaml
- id: fake-sensor
  type: simulated
  interface: simulated
  params:
    temp_min: 20.0      # optional — default 20.0
    temp_max: 30.0      # optional — default 30.0
    humidity_min: 40.0  # optional — default 40.0
    humidity_max: 80.0  # optional — default 80.0
```

| param | required | description |
|---|---|---|
| `temp_min` | no | Lower bound for random temperature. Default `20.0` |
| `temp_max` | no | Upper bound for random temperature. Default `30.0` |
| `humidity_min` | no | Lower bound for random humidity. Default `40.0` |
| `humidity_max` | no | Upper bound for random humidity. Default `80.0` |

`min` must be less than `max` for each pair.

Publishes: `temperature`, `humidity`

---

## `cameras`

Optional. Omitting this block entirely means mediamtx is never spawned and camera streaming is disabled. Camera IDs must be unique within the node.

`mediamtx` must be installed and on `PATH` — see the [install instructions](../README.md#camera-streaming-mediamtx).

```yaml
cameras:
  - id: canopy-cam    # unique name, becomes the RTSP stream path
    type: rpi_csi     # rpi_csi | usb | rtsp
    params:
      camera_id: 0
```

Each declared camera becomes an RTSP stream at `rtsp://<node-ip>:8554/<camera-id>`.

### Pi Camera Module (libcamera)

```yaml
- id: canopy-cam
  type: rpi_csi
  params:
    camera_id: 0   # required — rpicam index (0 for the first/only camera)
```

| param | required | description |
|---|---|---|
| `camera_id` | yes | libcamera device index. `0` for a single connected camera |

Requires mediamtx built with `rpiCamera` support (the standard release includes it).

### USB / V4L2 camera

```yaml
- id: usb-cam
  type: usb
  params:
    device: /dev/video0   # required — V4L2 device path
```

| param | required | description |
|---|---|---|
| `device` | yes | V4L2 device node, e.g. `/dev/video0` |

Streams via ffmpeg (`libx264`, ultrafast preset) publishing to the mediamtx RTSP endpoint. `ffmpeg` must be installed on the Pi.

### IP / RTSP camera

Re-publishes an existing RTSP stream through mediamtx, making it available alongside local cameras.

```yaml
- id: ip-cam
  type: rtsp
  params:
    url: rtsp://192.168.1.50/stream   # required — source RTSP URL
```

| param | required | description |
|---|---|---|
| `url` | yes | Full RTSP URL of the source stream |

---

## Full example

```yaml
node_id: tent-1
poll_interval: 30

mqtt:
  broker: 192.168.1.10
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

  - id: ambient
    type: tp358
    interface: bluetooth
    params:
      mac: "A4:C1:38:XX:XX:XX"
      scan_timeout: 15.0

cameras:
  - id: canopy-cam
    type: rpi_csi
    params:
      camera_id: 0
```
