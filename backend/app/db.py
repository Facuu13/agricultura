from collections.abc import Generator
from pathlib import Path
import subprocess
import sys
import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _connect_args(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    settings.database_url,
    connect_args=_connect_args(settings.database_url),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    alembic_bin = shutil.which("alembic") or str(Path(sys.executable).with_name("alembic"))
    subprocess.run(
        [
            alembic_bin,
            "-c",
            str(alembic_ini),
            "-x",
            f"db_url={settings.database_url}",
            "upgrade",
            "head",
        ],
        check=True,
    )
