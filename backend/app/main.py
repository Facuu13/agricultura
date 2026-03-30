import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import make_url

from app.config import settings
from app.db import init_db
from app.mqtt_service import MqttService
from app.routers import api
from app.ws_hub import WsHub

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def _ensure_sqlite_parent_dir(url: str) -> None:
    u = make_url(url)
    if u.drivername != "sqlite" or not u.database:
        return
    db_path = u.database
    if db_path.startswith("/") or (len(db_path) > 1 and db_path[1] == ":"):
        parent = Path(db_path).parent
    else:
        parent = Path(db_path).resolve().parent
    parent.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_sqlite_parent_dir(settings.database_url)
    init_db()
    hub = WsHub()
    loop = asyncio.get_running_loop()
    app.state.loop = loop
    app.state.ws_hub = hub
    mqtt_svc = MqttService(loop=loop, ws_hub=hub)
    app.state.mqtt_service = mqtt_svc
    mqtt_svc.start()
    log.info("Application started")
    yield
    mqtt_svc.stop()
    log.info("Application shutdown")


app = FastAPI(title="Agro station API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    hub: WsHub = app.state.ws_hub
    await hub.register(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.unregister(websocket)
