from fastapi import APIRouter
from services import influx

router = APIRouter()


@router.get("/latest")
def latest():
    return influx.get_latest()


@router.get("/{node_id}/{sensor_id}/{metric}")
def history(
    node_id: str,
    sensor_id: str,
    metric: str,
    start: str = "-1h",
    stop: str | None = None,
):
    return influx.get_history(node_id, sensor_id, metric, start, stop)
