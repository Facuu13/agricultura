# Copiar a config.py en el dispositivo y completar credenciales.

WIFI_SSID = "tu_red"
WIFI_PASSWORD = "tu_clave"

DEVICE_ID = "esp32-01"
MQTT_HOST = "192.168.1.100"
MQTT_PORT = 1883

# Failsafe: si True, regar en autonomía si humedad < umbral (sin MQTT)
FAILSAFE_AUTONOMOUS = False
SOIL_FAILSAFE_THRESHOLD = 25.0
RAIN_FAILSAFE_MAX_MM = 10.0

PUBLISH_INTERVAL_S = 30
