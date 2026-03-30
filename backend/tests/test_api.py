from datetime import datetime, timedelta

from app.db import SessionLocal
from app.models import Reading


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_sensors_empty(client):
    r = client.get("/sensors")
    assert r.status_code == 200
    assert r.json() == []


def test_sensors_latest_per_device(client):
    db = SessionLocal()
    try:
        db.add_all(
            [
                Reading(
                    device_id="d1",
                    soil_moisture=10.0,
                    rain_mm=0.0,
                    wind_speed=1.0,
                    radiation=100.0,
                    device_timestamp=1,
                ),
                Reading(
                    device_id="d1",
                    soil_moisture=50.0,
                    rain_mm=0.0,
                    wind_speed=2.0,
                    radiation=200.0,
                    device_timestamp=2,
                ),
                Reading(
                    device_id="d2",
                    soil_moisture=30.0,
                    rain_mm=1.0,
                    wind_speed=3.0,
                    radiation=300.0,
                    device_timestamp=3,
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    r = client.get("/sensors")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    by_id = {row["device_id"]: row for row in data}
    assert by_id["d1"]["soil_moisture"] == 50.0
    assert by_id["d2"]["soil_moisture"] == 30.0


def test_history_filter(client):
    db = SessionLocal()
    now = datetime.utcnow()
    try:
        db.add(
            Reading(
                device_id="hx",
                soil_moisture=20.0,
                rain_mm=0.1,
                wind_speed=4.0,
                radiation=500.0,
                device_timestamp=10,
                received_at=now - timedelta(hours=2),
            )
        )
        db.add(
            Reading(
                device_id="hx",
                soil_moisture=21.0,
                rain_mm=0.2,
                wind_speed=5.0,
                radiation=600.0,
                device_timestamp=11,
                received_at=now - timedelta(minutes=30),
            )
        )
        db.commit()
    finally:
        db.close()

    r = client.get("/history", params={"device_id": "hx"})
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 2
    assert rows[0]["soil_moisture"] == 20.0

    r2 = client.get(
        "/history",
        params={
            "device_id": "hx",
            "from_ts": (now - timedelta(hours=1)).isoformat(),
        },
    )
    assert r2.status_code == 200
    assert len(r2.json()) == 1


def test_post_actuator(client):
    r = client.post("/actuator", json={"device_id": "dev1", "valve": "ON"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["device_id"] == "dev1"
    assert body["valve"] == "ON"


def test_post_actuator_invalid_valve(client):
    r = client.post("/actuator", json={"device_id": "dev1", "valve": "MAYBE"})
    assert r.status_code == 422
