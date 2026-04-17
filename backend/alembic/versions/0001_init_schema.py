"""Initial schema.

Revision ID: 0001_init_schema
Revises:
Create Date: 2026-04-17 00:00:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_init_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.Column("soil_moisture", sa.Float(), nullable=False),
        sa.Column("rain_mm", sa.Float(), nullable=False),
        sa.Column("wind_speed", sa.Float(), nullable=False),
        sa.Column("radiation", sa.Float(), nullable=False),
        sa.Column("device_timestamp", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_readings_device_id", "readings", ["device_id"], unique=False)
    op.create_index("ix_readings_received_at", "readings", ["received_at"], unique=False)

    op.create_table(
        "irrigation_state",
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("last_on_unix", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("device_id"),
    )


def downgrade() -> None:
    op.drop_table("irrigation_state")
    op.drop_index("ix_readings_received_at", table_name="readings")
    op.drop_index("ix_readings_device_id", table_name="readings")
    op.drop_table("readings")
