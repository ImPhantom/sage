import os
from influxdb_client import InfluxDBClient

_client = InfluxDBClient(
    url=os.environ["INFLUXDB_URL"],
    token=os.environ["INFLUXDB_TOKEN"],
    org=os.environ["INFLUXDB_ORG"],
)
_query_api = _client.query_api()
_bucket = os.environ["INFLUXDB_BUCKET"]


def get_latest() -> list[dict]:
    query = f"""
from(bucket: "{_bucket}")
  |> range(start: -24h)
  |> last()
"""
    tables = _query_api.query(query)
    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "node_id": record.values.get("node_id"),
                "sensor_id": record.values.get("sensor_id"),
                "metric": record.get_measurement(),
                "value": record.get_value(),
                "time": record.get_time().isoformat(),
            })
    return results


def get_history(
    node_id: str,
    sensor_id: str,
    metric: str,
    start: str,
    stop: str | None,
) -> list[dict]:
    range_clause = f'start: {start}'
    if stop:
        range_clause += f', stop: {stop}'

    query = f"""
from(bucket: "{_bucket}")
  |> range({range_clause})
  |> filter(fn: (r) => r._measurement == "{metric}")
  |> filter(fn: (r) => r.node_id == "{node_id}")
  |> filter(fn: (r) => r.sensor_id == "{sensor_id}")
"""
    tables = _query_api.query(query)
    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "time": record.get_time().isoformat(),
                "value": record.get_value(),
            })
    return results


def get_nodes() -> list[dict]:
    query = f"""
from(bucket: "{_bucket}")
  |> range(start: -7d)
  |> last()
"""
    tables = _query_api.query(query)
    # collect max time per node_id
    nodes: dict[str, str] = {}
    for table in tables:
        for record in table.records:
            node_id = record.values.get("node_id")
            if node_id is None:
                continue
            ts = record.get_time().isoformat()
            if node_id not in nodes or ts > nodes[node_id]:
                nodes[node_id] = ts
    return [{"node_id": nid, "last_seen": ts} for nid, ts in sorted(nodes.items())]
