# Manual de usuario — panel web

Este documento describe el uso del **frontend** (dashboard) para supervisar la estación y accionar la válvula de riego.

## Acceso

1. Asegurate de que el **backend** esté en marcha (por ejemplo con Docker Compose; ver [README](../README.md)).
2. En otra terminal, iniciá el frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Abrí en el navegador la URL que muestra Vite (normalmente `http://localhost:5173`).

## Configuración en pantalla

| Campo | Uso |
|--------|-----|
| **URL API** | Dirección del servidor FastAPI (ej. `http://localhost:8001`). Al pulsar **Guardar y recargar** se guarda en el navegador (`localStorage`) y se recarga la página. |
| **Device ID** | Identificador del nodo (debe coincidir con el publicado por el ESP32 o el simulador, ej. `dev1`). |

También podés definir `VITE_API_BASE` en `frontend/.env` antes de `npm run dev` (ver `.env.example`).

## Qué muestra el panel

- **Tarjetas**: humedad de suelo (%), lluvia de la última lectura (mm), viento (m/s), radiación (W/m²).
- **Badge de riego**: con datos en tiempo real vía WebSocket indica si el servidor recomienda riego y el motivo (reglas del backend). Si solo hay datos de la API sin mensaje MQTT reciente, puede mostrarse “Sin datos en vivo”.
- **Estado WebSocket**: `open` indica conexión al canal en tiempo real; si falla, revisá la URL del API y el firewall.
- **Histórico**: gráfico de humedad y radiación obtenido con **Refrescar histórico** o al cambiar el dispositivo.
- **Control de válvula**: botones **ON** / **OFF** envían un comando manual por la API; el backend lo publica en MQTT para el nodo.

## Uso habitual

1. Verificá que **WebSocket** pase a `open`.
2. Elegí el **Device ID** correcto.
3. Observá las tarjetas y el badge; usá el gráfico para tendencias.
4. Para pruebas, usá **ON**/**OFF** solo cuando sepas que el actuador o la simulación están bajo control.

## Problemas frecuentes

| Síntoma | Qué revisar |
|---------|-------------|
| No cargan datos | URL API, que el backend responda en `GET /health`, CORS si el API no es el mismo origen. |
| WebSocket en `off` | Puerto bloqueado, URL mal escrita (http → ws en el mismo host/puerto). |
| Histórico vacío | Que existan lecturas para ese `device_id` (MQTT o simulador). |
| Error al pulsar ON/OFF | Backend caído o MQTT deshabilitado en el servidor (modo test). |

Para pruebas del sistema completo seguí la [guía de pruebas manuales](guia_pruebas_manuales.md).
