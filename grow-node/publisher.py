from __future__ import annotations

import logging
import time

import paho.mqtt.client as mqtt

from config import NodeConfig, SensorConfig
from drivers import REGISTRY, BaseSensor

log = logging.getLogger(__name__)


def build_sensors(config: NodeConfig) -> list[tuple[SensorConfig, BaseSensor]]:
    sensors: list[tuple[SensorConfig, BaseSensor]] = []
    for sensor_cfg in config.sensors:
        driver_class = REGISTRY.get(sensor_cfg.interface)
        if driver_class is None:
            available = sorted(REGISTRY.keys())
            raise ValueError(
                f"Sensor '{sensor_cfg.id}': interface '{sensor_cfg.interface}' has no "
                f"registered driver. Available interfaces: {available}"
            )
        driver = driver_class(sensor_cfg)
        log.info("Initialized %r", driver)
        sensors.append((sensor_cfg, driver))
    return sensors


def connect_mqtt(config: NodeConfig) -> mqtt.Client:
    client = mqtt.Client(client_id=config.mqtt.client_id)
    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.connect(config.mqtt.broker, config.mqtt.port, keepalive=60)
    client.loop_start()
    return client


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        log.info("MQTT connected")
    else:
        log.error("MQTT connection failed (rc=%d)", rc)


def _on_disconnect(client, userdata, rc):
    if rc != 0:
        log.warning("MQTT unexpected disconnect (rc=%d)", rc)


def publish_reading(
    client: mqtt.Client, node_id: str, sensor_id: str, reading: dict
) -> None:
    for metric, value in reading.items():
        topic = f"grows/{node_id}/{sensor_id}/{metric}"
        payload = str(round(float(value), 2))
        result = client.publish(topic, payload, qos=1, retain=False)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            log.warning("Publish failed: %s (rc=%d)", topic, result.rc)
        else:
            log.debug("Published %s = %s", topic, payload)


def run_publish_loop(config: NodeConfig) -> None:
    sensors = build_sensors(config)
    client = connect_mqtt(config)
    log.info(
        "Publish loop started: %d sensor(s), interval=%ds, broker=%s:%d",
        len(sensors), config.poll_interval, config.mqtt.broker, config.mqtt.port,
    )

    try:
        while True:
            for sensor_cfg, driver in sensors:
                try:
                    reading = driver.read()
                    publish_reading(client, config.node_id, sensor_cfg.id, reading)
                    log.info("[%s] %s", sensor_cfg.id, reading)
                except Exception as e:
                    log.error("[%s] Read failed: %s", sensor_cfg.id, e)
            time.sleep(config.poll_interval)
    except KeyboardInterrupt:
        log.info("Interrupted, shutting down")
    finally:
        client.loop_stop()
        client.disconnect()
