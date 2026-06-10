from dotenv import load_dotenv
load_dotenv()

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import readings, nodes, ws, agent
from services import mqtt


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt.start(asyncio.get_event_loop())
    yield
    mqtt.stop()


app = FastAPI(title="ai-botanist API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(readings.router, prefix="/readings")
app.include_router(nodes.router, prefix="/nodes")
app.include_router(ws.router)
app.include_router(agent.router, prefix="/agent")


@app.get("/health")
def health():
    return {"status": "ok"}
