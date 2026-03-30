#!/usr/bin/env python3
"""
Simula un nodo ESP32: publica telemetría en agro/<device_id>/data y opcionalmente
escucha comandos en agro/<device_id>/actuators (mismo formato que el firmware).

Ejemplo:
  pip install -r scripts/requirements.txt
  python scripts/simulate_esp32.py --host localhost --device dev1 --interval 5

Con Docker Compose (Mosquitto en el host en el puerto 1883):
  python scripts/simulate_esp32.py --host 127.0.0.1 --device esp32-01
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from typing import Any

import paho.mqtt.client as mqtt


def build_payload(t: float) -> dict[str, Any]:
    soil = 42.0 + 8.0 * math.sin(t / 17.0) + random.uniform(-1, 1)
    soil = max(5.0, min(95.0, soil))
    rain = max(0.0, (math.sin(t / 23.0) + 1.0) * 0.12)
    wind = 3.0 + abs(6.0 * math.sin(t / 11.0)) + random.uniform(0, 0.5)
    radiation = 350.0 + 450.0 * max(0.0, math.sin(t / 40.0))
    return {
        "soil_moisture": round(soil, 2),
        "rain_mm": round(rain, 3),
        "wind_speed": round(wind, 2),
        "radiation": round(radiation, 1),
        "timestamp": int(time.time()),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Simulador MQTT tipo ESP32 (agro/<id>/data)")
    p.add_argument("--host", default="127.0.0.1", help="Broker MQTT")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--device", default="dev1", help="device_id (topic agro/<device>/...)")
    p.add_argument("--interval", type=float, default=10.0, help="Segundos entre publicaciones")
    p.add_argument("--once", action="store_true", help="Publicar un solo mensaje y salir")
    p.add_argument(
        "--listen-actuators",
        action="store_true",
        help="Imprimir mensajes recibidos en agro/<device>/actuators",
    )
    args = p.parse_args()

    topic_data = f"agro/{args.device}/data"
    topic_act = f"agro/{args.device}/actuators"

    def on_message(_c: mqtt.Client, _u: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            payload = msg.payload.decode("utf-8")
            print(f"[actuators] {msg.topic} -> {payload}", flush=True)
        except Exception as e:
            print(f"[actuators] error: {e}", flush=True)

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"sim-{args.device}",
        protocol=mqtt.MQTTv311,
    )
    if args.listen_actuators:
        client.on_message = on_message

    try:
        client.connect(args.host, args.port, keepalive=30)
    except OSError as e:
        print(f"No se pudo conectar a {args.host}:{args.port}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.listen_actuators:
        client.subscribe(topic_act, qos=0)

    client.loop_start()

    t0 = time.time()
    try:
        while True:
            payload = build_payload(time.time() - t0)
            body = json.dumps(payload)
            client.publish(topic_data, body, qos=0)
            print(f"[data] {topic_data} {body}", flush=True)
            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nInterrumpido.", flush=True)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
