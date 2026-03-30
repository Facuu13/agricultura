"""Configurar entorno antes de importar la app (DB en tmp, MQTT desactivado)."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_tmpdir = tempfile.mkdtemp(prefix="agro_pytest_")
_db_path = Path(_tmpdir) / "test.db"
os.environ["ENABLE_MQTT"] = "false"
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path.resolve().as_posix()}"

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_db() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
