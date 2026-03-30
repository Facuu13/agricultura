import json
import time

import network
from machine import Pin  # type: ignore
from umqtt.simple import MQTTClient

try:
    import config
except ImportError:
    raise SystemExit("Crear config.py desde config_example.py")

try:
    import ntptime  # type: ignore
except ImportError:
    ntptime = None

import sensors_sim

try:
    LED = Pin(2, Pin.OUT)
except Exception:
    LED = None

_valve_on = False
_last_valve = "OFF"
_rain_accum_session = 0.0


def set_valve(on: bool) -> None:
    global _valve_on, _last_valve
    _valve_on = on
    _last_valve = "ON" if on else "OFF"
    if LED is not None:
        LED.value(1 if on else 0)
    print("[valve]", _last_valve)


def sync_time() -> None:
    if ntptime is None:
        return
    try:
        ntptime.settime()
        print("[ntp] ok")
    except OSError as e:
        print("[ntp] fail", e)


def connect_wifi() -> None:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        for _ in range(40):
            if wlan.isconnected():
                break
            time.sleep(0.5)
    if wlan.isconnected():
        print("[wifi]", wlan.ifconfig())
    else:
        print("[wifi] no conectado")


def make_mqtt() -> MQTTClient:
    cid = bytes(config.DEVICE_ID, "utf-8")
    return MQTTClient(cid, config.MQTT_HOST, port=config.MQTT_PORT, keepalive=60)


def topic_data() -> str:
    return "agro/{}/data".format(config.DEVICE_ID)


def topic_actuators() -> str:
    return "agro/{}/actuators".format(config.DEVICE_ID)


def publish_payload(client: MQTTClient) -> None:
    soil, rain, wind, rad = sensors_sim.read_simulated()
    try:
        ts = int(time.time())
    except Exception:
        ts = 0
    payload = {
        "soil_moisture": round(soil, 2),
        "rain_mm": round(rain, 3),
        "wind_speed": round(wind, 2),
        "radiation": round(rad, 1),
        "timestamp": ts,
    }
    client.publish(topic_data(), json.dumps(payload))


def apply_failsafe(soil: float, rain_inc: float) -> None:
    global _rain_accum_session
    _rain_accum_session += rain_inc
    if not getattr(config, "FAILSAFE_AUTONOMOUS", False):
        return
    if soil < getattr(config, "SOIL_FAILSAFE_THRESHOLD", 25.0) and _rain_accum_session < getattr(
        config, "RAIN_FAILSAFE_MAX_MM", 10.0
    ):
        set_valve(True)
    else:
        set_valve(False)


def on_actuator_message(topic: bytes, msg: bytes) -> None:
    try:
        data = json.loads(msg.decode())
        v = str(data.get("valve", "")).upper()
        if v == "ON":
            set_valve(True)
        elif v == "OFF":
            set_valve(False)
    except Exception as e:
        print("[actuator] parse error", e)


def run_loop() -> None:
    connect_wifi()
    sync_time()
    interval = int(getattr(config, "PUBLISH_INTERVAL_S", 30))

    while True:
        try:
            client = make_mqtt()
            client.set_callback(on_actuator_message)
            client.connect()
            client.subscribe(topic_actuators())
            print("[mqtt] connected")

            while True:
                publish_payload(client)
                deadline = time.time() + interval
                while time.time() < deadline:
                    try:
                        client.check_msg()
                    except OSError:
                        raise
                    time.sleep(0.2)
        except OSError as e:
            print("[mqtt] error", e)
            soil, rain, _, _ = sensors_sim.read_simulated()
            apply_failsafe(soil, rain)
            if not getattr(config, "FAILSAFE_AUTONOMOUS", False):
                set_valve(_valve_on)
            print("[failsafe] último estado válvula:", _last_valve)
            time.sleep(5)


if __name__ == "__main__":
    run_loop()
