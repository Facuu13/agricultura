from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Reading
from app.config import settings
from app.schemas import ActuatorCommand, HistoryPoint, ReadingOut

router = APIRouter(tags=["api"])


def require_actuator_api_key(x_api_key: str | None = Header(default=None)) -> None:
    configured_api_key = settings.actuator_api_key
    if not configured_api_key:
        return
    if x_api_key != configured_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/sensors", response_model=list[ReadingOut])
def get_sensors(db: Session = Depends(get_db)) -> list[Reading]:
    subq = (
        select(Reading.device_id, func.max(Reading.id).label("max_id"))
        .group_by(Reading.device_id)
        .subquery()
    )
    q = select(Reading).join(subq, Reading.id == subq.c.max_id)
    rows = db.execute(q).scalars().all()
    return list(rows)


@router.get("/history", response_model=list[HistoryPoint])
def get_history(
    device_id: str,
    db: Session = Depends(get_db),
    from_ts: datetime | None = Query(None),
    to_ts: datetime | None = Query(None),
) -> list[Reading]:
    q = select(Reading).where(Reading.device_id == device_id).order_by(Reading.received_at.asc())
    if from_ts is not None:
        q = q.where(Reading.received_at >= from_ts)
    if to_ts is not None:
        q = q.where(Reading.received_at <= to_ts)
    rows = db.execute(q).scalars().all()
    return list(rows)


@router.post("/actuator")
def post_actuator(
    body: ActuatorCommand,
    request: Request,
    _: None = Depends(require_actuator_api_key),
) -> dict:
    mqtt = getattr(request.app.state, "mqtt_service", None)
    if mqtt is None:
        raise HTTPException(status_code=503, detail="MQTT not available")
    mqtt.publish_actuator(body.device_id, body.valve)
    loop = request.app.state.loop
    hub = request.app.state.ws_hub
    if loop and hub:
        import asyncio

        asyncio.run_coroutine_threadsafe(
            hub.broadcast(
                {
                    "type": "actuator_manual",
                    "payload": {
                        "device_id": body.device_id,
                        "valve": body.valve,
                    },
                }
            ),
            loop,
        )
    return {"ok": True, "device_id": body.device_id, "valve": body.valve}
