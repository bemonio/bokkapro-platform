"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-02-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "offices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("storage_capacity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("lat >= -90 AND lat <= 90", name="ck_offices_lat"),
        sa.CheckConstraint("lng >= -180 AND lng <= 180", name="ck_offices_lng"),
        sa.CheckConstraint("storage_capacity >= 0", name="ck_offices_storage_capacity"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_offices_uuid", "offices", ["uuid"], unique=False)
    op.create_index("ix_offices_tenant_id", "offices", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_offices_tenant_id", table_name="offices")
    op.drop_index("ix_offices_uuid", table_name="offices")
    op.drop_table("offices")
