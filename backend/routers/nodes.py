from fastapi import APIRouter
from pydantic import BaseModel
from services import influx, go2rtc

router = APIRouter()


class Camera(BaseModel):
    id: str
    rtsp_url: str


@router.post("/{node_id}/cameras", status_code=204)
def register_cameras(node_id: str, cameras: list[Camera]):
    go2rtc.register_node_cameras(node_id, [c.model_dump() for c in cameras])


@router.get("")
def nodes():
    node_list = influx.get_nodes()
    camera_map = go2rtc.get_cameras()
    for node in node_list:
        node["cameras"] = camera_map.get(node["node_id"], [])
    return node_list
