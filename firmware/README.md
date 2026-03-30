# Firmware ESP32 (MicroPython)

1. Flashear MicroPython en el ESP32 (documentación oficial del chip).
2. Copiar `config_example.py` a `config.py` y definir `WIFI_*`, `DEVICE_ID`, `MQTT_HOST` (misma red que el broker).
3. Copiar al dispositivo: `main.py`, `sensors_sim.py`, `config.py`.

El firmware publica en `agro/<DEVICE_ID>/data` y escucha `agro/<DEVICE_ID>/actuators`.

Con `FAILSAFE_AUTONOMOUS = True` en `config.py`, si falla MQTT se aplica riego local según umbrales; si es `False`, se mantiene el último estado de la válvula.
