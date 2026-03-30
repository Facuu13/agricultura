# Guía de pruebas manuales

Checklist para validar el sistema extremo a extremo. Marcá cada ítem cuando pase.

## Preparación

- [ ] `docker compose up -d --build` sin errores.
- [ ] `curl -s http://localhost:8001/health` devuelve `{"status":"ok"}` (ajustá el puerto si cambiaste el mapeo).
- [ ] Frontend: `cd frontend && npm run dev`, página carga sin errores en consola del navegador.
- [ ] En el panel, **URL API** = `http://localhost:8001` (o el puerto que uses) y **Guardar y recargar**.

## MQTT y backend

- [ ] Con Mosquitto arriba, publicar un mensaje de prueba (desde contenedor o `mosquitto_pub` local):

  ```bash
  docker exec $(docker ps -q -f name=mosquitto) mosquitto_pub -h localhost \
    -t 'agro/dev1/data' \
    -m '{"soil_moisture":22,"rain_mm":0,"wind_speed":4,"radiation":750,"timestamp":1710000000}'
  ```

- [ ] `curl -s 'http://localhost:8001/sensors' | jq` incluye `device_id` `dev1` con esos valores (aprox.).
- [ ] `curl -s 'http://localhost:8001/history?device_id=dev1' | jq` devuelve al menos una entrada.

## Riego automático (lógica v1)

Con datos que cumplan: humedad &lt; 30 %, poca lluvia en 24 h en BD, radiación alta:

- [ ] Tras publicar telemetría adecuada, el backend publica en `agro/dev1/actuators` (observar con suscriptor):

  ```bash
  docker exec -it $(docker ps -q -f name=mosquitto) mosquitto_sub -h localhost -t 'agro/dev1/actuators' -C 1
  ```

  (En otra terminal dispará otra publicación a `data` si hace falta.)

- [ ] Con humedad alta o lluvia acumulada alta, el comando esperado es `OFF` o no se fuerza riego según tu configuración.

## WebSocket y panel

- [ ] **Device ID** = `dev1`.
- [ ] Estado **WebSocket** = `open`.
- [ ] Tras publicar otra vez a `agro/dev1/data`, las tarjetas se actualizan sin recargar la página.
- [ ] **Refrescar histórico** muestra puntos en el gráfico.

## Control manual

- [ ] Botón **ON**: `POST /actuator` correcto (red 200 en herramientas de red del navegador).
- [ ] Con `mosquitto_sub` en `agro/dev1/actuators` aparece `{"valve": "ON"}` (o `OFF` al pulsar **OFF**).

## Simulador Python

- [ ] `pip install -r scripts/requirements.txt`
- [ ] `python scripts/simulate_esp32.py --host 127.0.0.1 --device dev1 --once`
- [ ] `GET /sensors` refleja el `device_id` `dev1` actualizado.
- [ ] Opcional: `python scripts/simulate_esp32.py --host 127.0.0.1 --device dev1 --listen-actuators --interval 15` y comprobar que al cumplirse condiciones de riego se imprimen comandos en consola.

## Firmware real (cuando exista)

- [ ] ESP32 en la misma red que el broker; `config.py` con `MQTT_HOST` correcto.
- [ ] En logs del dispositivo aparecen publicaciones y cambios de válvula al recibir MQTT.
- [ ] Desconectar WiFi o broker: comportamiento acorde a failsafe (último estado o autónomo según `config.py`).

## Regresión rápida tras cambios

- [ ] `cd backend && pytest -q`
- [ ] `cd frontend && npm test && npm run build`
