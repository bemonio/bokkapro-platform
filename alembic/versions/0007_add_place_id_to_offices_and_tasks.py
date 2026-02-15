"""add place_id to offices and tasks

Revision ID: 0007_add_place_id_to_offices_and_tasks
Revises: 0006_add_route_tasks_table
Create Date: 2026-02-15 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0007_add_place_id_to_offices_and_tasks"
down_revision: str | None = "0006_add_route_tasks_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("offices", sa.Column("place_id", sa.String(), nullable=True))
    op.create_index(op.f("ix_offices_place_id"), "offices", ["place_id"], unique=False)

    op.add_column("tasks", sa.Column("place_id", sa.String(), nullable=True))
    op.create_index(op.f("ix_tasks_place_id"), "tasks", ["place_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_place_id"), table_name="tasks")
    op.drop_column("tasks", "place_id")

    op.drop_index(op.f("ix_offices_place_id"), table_name="offices")
    op.drop_column("offices", "place_id")
