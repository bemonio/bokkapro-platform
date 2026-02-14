"""add tasks table

Revision ID: 0004_add_tasks_table
Revises: 0003_add_vehicle_coordinates
Create Date: 2026-02-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_add_tasks_table"
down_revision: str | None = "0003_add_vehicle_coordinates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("office_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("time_window_start", sa.DateTime(), nullable=True),
        sa.Column("time_window_end", sa.DateTime(), nullable=True),
        sa.Column("service_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("load_units", sa.Integer(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("reference", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["office_id"], ["offices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_deleted_at"), "tasks", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_tasks_office_id"), "tasks", ["office_id"], unique=False)
    op.create_index(op.f("ix_tasks_priority"), "tasks", ["priority"], unique=False)
    op.create_index(op.f("ix_tasks_reference"), "tasks", ["reference"], unique=False)
    op.create_index(op.f("ix_tasks_status"), "tasks", ["status"], unique=False)
    op.create_index(op.f("ix_tasks_tenant_id"), "tasks", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_tasks_type"), "tasks", ["type"], unique=False)
    op.create_index(op.f("ix_tasks_uuid"), "tasks", ["uuid"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_uuid"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_type"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_tenant_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_status"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_reference"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_priority"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_office_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_deleted_at"), table_name="tasks")
    op.drop_table("tasks")
