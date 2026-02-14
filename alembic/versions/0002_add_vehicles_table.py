"""add vehicles table

Revision ID: 0002_add_vehicles_table
Revises: 0001_initial_schema
Create Date: 2026-02-14 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_add_vehicles_table"
down_revision: Union[str, Sequence[str], None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("office_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("plate", sa.String(), nullable=True),
        sa.Column("max_capacity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("max_capacity >= 0", name="ck_vehicles_max_capacity"),
        sa.ForeignKeyConstraint(["office_id"], ["offices.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_vehicles_uuid", "vehicles", ["uuid"], unique=False)
    op.create_index("ix_vehicles_tenant_id", "vehicles", ["tenant_id"], unique=False)
    op.create_index("ix_vehicles_office_id", "vehicles", ["office_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_vehicles_office_id", table_name="vehicles")
    op.drop_index("ix_vehicles_tenant_id", table_name="vehicles")
    op.drop_index("ix_vehicles_uuid", table_name="vehicles")
    op.drop_table("vehicles")
