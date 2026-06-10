from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services import mqtt

router = APIRouter()


@router.websocket("/ws/live")
async def ws_live(websocket: WebSocket) -> None:
    await websocket.accept()
    mqtt.connected_websockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        mqtt.connected_websockets.discard(websocket)
