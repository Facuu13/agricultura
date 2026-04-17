# Manual técnico y de operación

Arquitectura: **nodo (ESP32)** ↔ **MQTT (Mosquitto)** ↔ **backend (FastAPI + SQLite)** ↔ **frontend (React)**.

## Topics MQTT

| Dirección | Topic | Payload (JSON) |
|-----------|--------|----------------|
| Nodo → broker | `agro/<device_id>/data` | `soil_moisture`, `rain_mm`, `wind_speed`, `radiation`, `timestamp` |
| Servidor → nodo | `agro/<device_id>/actuators` | `{"valve":"ON"}` o `{"valve":"OFF"}` |

No se usa barra inicial en el topic (`/agro/...`); la convención del proyecto es `agro/...`.

## Backend

### Arranque con Docker (recomendado)

```bash
docker compose up -d --build
```

- API en `http://localhost:8001` (puerto host; el contenedor escucha en 8000).
- Mosquitto en `1883`.

### Variables de entorno relevantes

Definibles en `docker-compose.yml` o `.env` del backend:

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | SQLite por defecto (`sqlite:////data/agro.db` en contenedor). |
| `MQTT_HOST` | Hostname del broker (en Compose: `mosquitto`). |
| `MQTT_PORT` | Puerto del broker (1883). |
| `MQTT_USERNAME` / `MQTT_PASSWORD` | Credenciales del broker (opcional en desarrollo, recomendado en producción). |
| `ACTUATOR_API_KEY` | Si está definida, `POST /actuator` exige header `x-api-key`. |
| `CORS_ORIGINS` | JSON array, ej. `["http://localhost:5173"]`. |
| `ENABLE_MQTT` | `true`/`false`. Si `false`, no se conecta al broker; `POST /actuator` sigue respondiendo pero no publica (útil para tests). |

Umbrales de riego: `SOIL_MOISTURE_THRESHOLD`, `RAIN_SUM_24H_MAX_MM`, `RADIATION_THRESHOLD`, `MIN_SECONDS_BETWEEN_IRRIGATION_ON` (ver `backend/app/config.py`).

### API REST

- `GET /health` — estado del servicio.
- `GET /sensors` — última lectura por `device_id`.
- `GET /history?device_id=...&from_ts=...&to_ts=...` — serie temporal (fechas ISO opcionales).
- `POST /actuator` — cuerpo `{"device_id":"...","valve":"ON"|"OFF"}`.
- WebSocket `GET ws://<host>/ws` — eventos `reading` y `actuator_manual` en JSON.

### Lógica de riego (v1)

Tras cada lectura guardada: si humedad &lt; umbral **y** suma de `rain_mm` en 24 h &lt; máximo **y** radiación &gt; umbral **y** no hay cooldown, se publica `valve: ON`; si no, `OFF`. Ajustá umbrales por entorno.

## Firmware (ESP32)

Ver [firmware/README.md](../firmware/README.md). Archivo `config.py` (no versionar secretos) con WiFi y `MQTT_HOST` apuntando al broker accesible en la red.

## Simulador de nodo (sin hardware)

```bash
pip install -r scripts/requirements.txt
python scripts/simulate_esp32.py --host 127.0.0.1 --device dev1 --interval 5
```

Opciones útiles: `--once`, `--listen-actuators` (ver comandos que envía el servidor).

## Tests automáticos

- Backend: `cd backend && pip install -r requirements-dev.txt && pytest`.
- Frontend: `cd frontend && npm test`.

## Copias y base de datos

El fichero SQLite en Docker vive en el volumen `backend_data`. Para backup, copiar el `.db` con el contenedor detenido o usar `docker compose exec` y volcar el archivo.

## Seguridad (producción)

La configuración actual `mosquitto.conf` permite anónimos: **solo para desarrollo**.

Para hardening:

1. Montar `mosquitto/mosquitto.secure.conf` en lugar de `mosquitto.conf`.
2. Crear archivos `mosquitto/passwords` y `mosquitto/acl` a partir de `passwords.example` y `acl.example`.
3. Configurar `MQTT_USERNAME` y `MQTT_PASSWORD` en backend.
4. Definir `ACTUATOR_API_KEY` y usar `x-api-key` desde clientes autorizados.
5. Publicar API detrás de HTTPS/reverse proxy.
