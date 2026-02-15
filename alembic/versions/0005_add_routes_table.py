"""add routes table

Revision ID: 0005_add_routes_table
Revises: 0004_add_tasks_table
Create Date: 2026-02-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_add_routes_table"
down_revision: str | None = "0004_add_tasks_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("office_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("total_tasks", sa.Integer(), nullable=False),
        sa.Column("total_distance_m", sa.Integer(), nullable=True),
        sa.Column("total_duration_s", sa.Integer(), nullable=True),
        sa.Column("total_load", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["office_id"], ["offices.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_routes_deleted_at"), "routes", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_routes_office_id"), "routes", ["office_id"], unique=False)
    op.create_index(op.f("ix_routes_service_date"), "routes", ["service_date"], unique=False)
    op.create_index(op.f("ix_routes_status"), "routes", ["status"], unique=False)
    op.create_index(op.f("ix_routes_tenant_id"), "routes", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_routes_uuid"), "routes", ["uuid"], unique=True)
    op.create_index(op.f("ix_routes_vehicle_id"), "routes", ["vehicle_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_routes_vehicle_id"), table_name="routes")
    op.drop_index(op.f("ix_routes_uuid"), table_name="routes")
    op.drop_index(op.f("ix_routes_tenant_id"), table_name="routes")
    op.drop_index(op.f("ix_routes_status"), table_name="routes")
    op.drop_index(op.f("ix_routes_service_date"), table_name="routes")
    op.drop_index(op.f("ix_routes_office_id"), table_name="routes")
    op.drop_index(op.f("ix_routes_deleted_at"), table_name="routes")
    op.drop_table("routes")
