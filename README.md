# Estación agrometeorológica inteligente

Monorepo: **firmware** (ESP32 + MicroPython), **backend** (FastAPI + MQTT + SQLite) y **frontend** (React + Vite).

## Requisitos

- Docker y Docker Compose (broker Mosquitto + API)
- Node.js 20+ para el frontend en desarrollo
- Python 3.12+ si ejecutás el backend sin Docker

## Backend y MQTT

Desde la raíz del repo:

```bash
docker compose up -d --build
```

- API: `http://localhost:8001` (mapeo `8001:8000` en [docker-compose.yml](docker-compose.yml); si el puerto 8000 está libre podés cambiarlo a `8000:8000`).
- Mosquitto: `localhost:1883`
- Variables útiles: `DATABASE_URL`, `MQTT_HOST`, `MQTT_PORT`, `CORS_ORIGINS` (ver [backend/app/config.py](backend/app/config.py)).

Endpoints: `GET /health`, `GET /sensors`, `GET /history?device_id=...`, `POST /actuator`, WebSocket `ws://localhost:8001/ws`.

## Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Ajustá `VITE_API_BASE` o usá el campo “URL API” en la UI (se guarda en `localStorage`).

## Firmware (ESP32)

1. Instalar [MicroPython](https://micropython.org/) en el ESP32.
2. Copiar `firmware/config_example.py` a `config.py` y completar WiFi y `MQTT_HOST` (IP de tu PC o del servidor con Mosquitto).
3. Subir `main.py`, `sensors_sim.py` y `config.py` al dispositivo.

## Prueba rápida sin hardware

Con el stack Docker levantado, publicar telemetría de prueba:

```bash
docker exec $(docker ps -q -f name=mosquitto) mosquitto_pub -h localhost \
  -t 'agro/dev1/data' \
  -m '{"soil_moisture":20,"rain_mm":0,"wind_speed":5,"radiation":800,"timestamp":1710000000}'
```

Luego abrí el frontend y usá `device_id` `dev1`.
