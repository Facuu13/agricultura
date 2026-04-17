# Matriz mínima de pruebas de confiabilidad

Objetivo: cubrir regresiones críticas en MQTT, WebSocket, riego y control manual.

## Backend (pytest)

1. **Autenticación de actuador**
   - Caso: `ACTUATOR_API_KEY` configurada y request sin `x-api-key`.
   - Esperado: `401`.
2. **Payload inválido de sensores**
   - Caso: `soil_moisture > 100`, valores negativos o fuera de rango.
   - Esperado: descartar payload, no persistir lectura.
3. **Cooldown persistente**
   - Caso: dos decisiones consecutivas con mismas condiciones favorables.
   - Esperado: primera `ON`, segunda `cooldown_active`.
4. **WebSocket disponible**
   - Caso: conexión a `/ws`.
   - Esperado: handshake exitoso sin excepción.

## Frontend (manual o e2e)

1. **Reconexión WebSocket**
   - Caso: detener backend por 10-20 s y volver a levantar.
   - Esperado: estado pasa por `off/connecting` y vuelve a `open`.
2. **Timeout de API**
   - Caso: backend no responde.
   - Esperado: mensaje de error claro `Request timeout`.
3. **Control manual con API key**
   - Caso: enviar ON/OFF sin key y con key.
   - Esperado: error sin key; éxito con key válida.

## Criterios de salida

- Tests backend pasan en CI.
- Frontend lint/test/build pasan en CI.
- No regresión en flujo end-to-end (`simulador -> MQTT -> backend -> dashboard`).
