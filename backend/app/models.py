from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    soil_moisture: Mapped[float] = mapped_column(Float)
    rain_mm: Mapped[float] = mapped_column(Float)
    wind_speed: Mapped[float] = mapped_column(Float)
    radiation: Mapped[float] = mapped_column(Float)
    device_timestamp: Mapped[int | None] = mapped_column(Integer, nullable=True)


class IrrigationState(Base):
    __tablename__ = "irrigation_state"

    device_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    last_on_unix: Mapped[int | None] = mapped_column(Integer, nullable=True)
