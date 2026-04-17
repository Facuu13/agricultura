import pytest
from pydantic import ValidationError

from app.schemas import ActuatorCommand, SensorPayload


def test_sensor_payload_rejects_out_of_range_values():
    with pytest.raises(ValidationError):
        SensorPayload(
            soil_moisture=120.0,
            rain_mm=0.0,
            wind_speed=2.0,
            radiation=800.0,
        )


def test_actuator_device_id_rejects_invalid_characters():
    with pytest.raises(ValidationError):
        ActuatorCommand(device_id="dev 1", valve="ON")
