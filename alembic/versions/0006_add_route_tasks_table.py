"""add route tasks table

Revision ID: 0006_add_route_tasks_table
Revises: 0005_add_routes_table
Create Date: 2026-02-15 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_add_route_tasks_table"
down_revision: str | None = "0005_add_routes_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "route_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("route_uuid", sa.String(), nullable=False),
        sa.Column("task_uuid", sa.String(), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("planned_arrival_at", sa.DateTime(), nullable=True),
        sa.Column("planned_departure_at", sa.DateTime(), nullable=True),
        sa.Column("actual_arrival_at", sa.DateTime(), nullable=True),
        sa.Column("actual_departure_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["route_uuid"], ["routes.uuid"]),
        sa.ForeignKeyConstraint(["task_uuid"], ["tasks.uuid"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("route_uuid", "sequence_order", name="uq_route_tasks_route_sequence"),
        sa.UniqueConstraint("route_uuid", "task_uuid", name="uq_route_tasks_route_task"),
    )
    op.create_index(op.f("ix_route_tasks_deleted_at"), "route_tasks", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_route_tasks_route_uuid"), "route_tasks", ["route_uuid"], unique=False)
    op.create_index(op.f("ix_route_tasks_sequence_order"), "route_tasks", ["sequence_order"], unique=False)
    op.create_index(op.f("ix_route_tasks_status"), "route_tasks", ["status"], unique=False)
    op.create_index(op.f("ix_route_tasks_task_uuid"), "route_tasks", ["task_uuid"], unique=False)
    op.create_index(op.f("ix_route_tasks_tenant_id"), "route_tasks", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_route_tasks_uuid"), "route_tasks", ["uuid"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_route_tasks_uuid"), table_name="route_tasks")
    op.drop_index(op.f("ix_route_tasks_tenant_id"), table_name="route_tasks")
    op.drop_index(op.f("ix_route_tasks_task_uuid"), table_name="route_tasks")
    op.drop_index(op.f("ix_route_tasks_status"), table_name="route_tasks")
    op.drop_index(op.f("ix_route_tasks_sequence_order"), table_name="route_tasks")
    op.drop_index(op.f("ix_route_tasks_route_uuid"), table_name="route_tasks")
    op.drop_index(op.f("ix_route_tasks_deleted_at"), table_name="route_tasks")
    op.drop_table("route_tasks")
