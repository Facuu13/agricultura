import time
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Reading


@dataclass
class IrrigationDecision:
    should_irrigate: bool
    reason: str


_last_on_monotonic: dict[str, float] = {}


def sum_rain_last_24h(db: Session, device_id: str) -> float:
    from datetime import datetime, timedelta

    since = datetime.utcnow() - timedelta(hours=24)
    q = select(func.coalesce(func.sum(Reading.rain_mm), 0.0)).where(
        Reading.device_id == device_id,
        Reading.received_at >= since,
    )
    return float(db.execute(q).scalar_one())


def evaluate_irrigation(
    db: Session,
    device_id: str,
    soil_moisture: float,
    radiation: float,
) -> IrrigationDecision:
    rain_sum = sum_rain_last_24h(db, device_id)
    now_m = time.monotonic()
    last_on = _last_on_monotonic.get(device_id, 0.0)

    if soil_moisture >= settings.soil_moisture_threshold:
        return IrrigationDecision(False, "soil_moisture_above_threshold")
    if rain_sum >= settings.rain_sum_24h_max_mm:
        return IrrigationDecision(False, "rain_24h_above_max")
    if radiation <= settings.radiation_threshold:
        return IrrigationDecision(False, "radiation_below_threshold")
    if now_m - last_on < settings.min_seconds_between_irrigation_on:
        return IrrigationDecision(False, "cooldown_active")

    _last_on_monotonic[device_id] = now_m
    return IrrigationDecision(True, "conditions_met")


def valve_command_from_decision(decision: IrrigationDecision) -> str:
    return "ON" if decision.should_irrigate else "OFF"
