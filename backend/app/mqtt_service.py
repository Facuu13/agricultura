import asyncio
import json
import logging
import re
import threading
from typing import TYPE_CHECKING, Any

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.irrigation import evaluate_irrigation, valve_command_from_decision
from app.models import Reading
from app.schemas import SensorPayload

if TYPE_CHECKING:
    from app.ws_hub import WsHub

log = logging.getLogger(__name__)

_TOPIC_DATA = re.compile(r"^agro/([^/]+)/data$")


class MqttService:
    def __init__(
        self,
        loop: "asyncio.AbstractEventLoop | None",
        ws_hub: "WsHub",
    ) -> None:
        self._loop = loop
        self._ws_hub = ws_hub
        self._client: mqtt.Client | None = None
        self._thread: threading.Thread | None = None

    def _schedule_ws(self, message: dict) -> None:
        if self._loop is None:
            return
        try:
            asyncio.run_coroutine_threadsafe(self._ws_hub.broadcast(message), self._loop)
        except RuntimeError:
            log.exception("WebSocket broadcast scheduling failed")

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: dict[str, int],
        reason_code: Any,
        properties: Any,
    ) -> None:
        if getattr(reason_code, "is_failure", False):
            log.error("MQTT connect failed: %s", reason_code)
            return
        client.subscribe("agro/+/data", qos=0)
        log.info("MQTT subscribed to agro/+/data")

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage,
    ) -> None:
        try:
            text = msg.payload.decode("utf-8")
            topic = msg.topic or ""
            m = _TOPIC_DATA.match(topic)
            if not m:
                return
            device_id = m.group(1)
            data = json.loads(text)
            payload = SensorPayload.model_validate(data)
        except Exception:
            log.exception("Invalid MQTT payload")
            return

        db = SessionLocal()
        try:
            reading = Reading(
                device_id=device_id,
                soil_moisture=payload.soil_moisture,
                rain_mm=payload.rain_mm,
                wind_speed=payload.wind_speed,
                radiation=payload.radiation,
                device_timestamp=payload.timestamp,
            )
            db.add(reading)
            db.commit()
            db.refresh(reading)

            decision = evaluate_irrigation(
                db,
                device_id,
                payload.soil_moisture,
                payload.radiation,
            )
            valve = valve_command_from_decision(decision)
            out_topic = settings.mqtt_topic_actuators_template.format(device_id=device_id)
            cmd = json.dumps({"valve": valve})
            client.publish(out_topic, cmd, qos=0)

            self._schedule_ws(
                {
                    "type": "reading",
                    "payload": {
                        "device_id": device_id,
                        "soil_moisture": reading.soil_moisture,
                        "rain_mm": reading.rain_mm,
                        "wind_speed": reading.wind_speed,
                        "radiation": reading.radiation,
                        "received_at": reading.received_at.isoformat() + "Z",
                        "irrigation_recommended": decision.should_irrigate,
                        "irrigation_reason": decision.reason,
                        "valve_auto": valve,
                    },
                }
            )
        finally:
            db.close()

    def start(self) -> None:
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="agro-backend",
            protocol=mqtt.MQTTv311,
        )
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.connect_async(settings.mqtt_host, settings.mqtt_port, keepalive=60)

        def loop_forever() -> None:
            client.loop_forever(retry_first_connection=True)

        self._client = client
        self._thread = threading.Thread(target=loop_forever, daemon=True)
        self._thread.start()
        log.info("MQTT client thread started")

    def publish_actuator(self, device_id: str, valve: str) -> None:
        if self._client is None:
            raise RuntimeError("MQTT client not started")
        topic = settings.mqtt_topic_actuators_template.format(device_id=device_id)
        self._client.publish(topic, json.dumps({"valve": valve}), qos=0)

    def stop(self) -> None:
        if self._client is not None:
            self._client.disconnect()
            self._client = None
