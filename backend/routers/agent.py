from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list


@router.post("/chat")
def chat(body: ChatRequest):
    return {"response": "Agent not yet implemented"}
