from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.irrigation import evaluate_irrigation, sum_rain_last_24h
from app.models import Reading


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_sum_rain_last_24h():
    db = _session()
    try:
        now = datetime.utcnow()
        db.add(
            Reading(
                device_id="r1",
                soil_moisture=40.0,
                rain_mm=1.0,
                wind_speed=0.0,
                radiation=100.0,
                received_at=now - timedelta(hours=1),
            )
        )
        db.add(
            Reading(
                device_id="r1",
                soil_moisture=40.0,
                rain_mm=2.5,
                wind_speed=0.0,
                radiation=100.0,
                received_at=now - timedelta(hours=25),
            )
        )
        db.commit()
        assert sum_rain_last_24h(db, "r1") == 1.0
    finally:
        db.close()


def test_evaluate_irrigation_dry_high_rad_low_rain():
    db = _session()
    try:
        now = datetime.utcnow()
        db.add(
            Reading(
                device_id="i1",
                soil_moisture=50.0,
                rain_mm=0.5,
                wind_speed=0.0,
                radiation=100.0,
                received_at=now - timedelta(hours=1),
            )
        )
        db.commit()
        d = evaluate_irrigation(db, "i1", soil_moisture=20.0, radiation=800.0)
        assert d.should_irrigate is True
        assert d.reason == "conditions_met"
    finally:
        db.close()


def test_evaluate_irrigation_wet_soil():
    db = _session()
    try:
        d = evaluate_irrigation(db, "x", soil_moisture=50.0, radiation=800.0)
        assert d.should_irrigate is False
        assert d.reason == "soil_moisture_above_threshold"
    finally:
        db.close()
