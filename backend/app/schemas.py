from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SensorPayload(BaseModel):
    soil_moisture: float = Field(..., ge=0.0, le=100.0)
    rain_mm: float = Field(..., ge=0.0, le=500.0)
    wind_speed: float = Field(..., ge=0.0, le=100.0)
    radiation: float = Field(..., ge=0.0, le=2000.0)
    timestamp: int | None = None


class ReadingOut(BaseModel):
    device_id: str
    received_at: datetime
    soil_moisture: float
    rain_mm: float
    wind_speed: float
    radiation: float
    device_timestamp: int | None

    model_config = {"from_attributes": True}


class HistoryPoint(BaseModel):
    received_at: datetime
    soil_moisture: float
    rain_mm: float
    wind_speed: float
    radiation: float


class ActuatorCommand(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    valve: Literal["ON", "OFF"]


class WsMessage(BaseModel):
    type: str
    payload: dict
