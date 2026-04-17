# Migraciones de base de datos (Alembic)

El backend ahora inicializa esquema con Alembic al arrancar (`upgrade head`).

## Flujo recomendado

1. Crear migración:

```bash
cd backend
alembic revision -m "descripcion_cambio"
```

2. Editar `upgrade()`/`downgrade()` en `backend/alembic/versions/*.py`.

3. Aplicar migraciones localmente:

```bash
alembic upgrade head
```

4. Verificar downgrade en entorno de pruebas:

```bash
alembic downgrade -1
alembic upgrade head
```

## Estrategia de despliegue sin pérdida

- Hacer backup del SQLite antes del despliegue.
- Ejecutar migraciones durante ventana de mantenimiento.
- Mantener migraciones idempotentes y reversibles.
- Validar endpoints críticos (`/sensors`, `/history`, `/actuator`) post-upgrade.
