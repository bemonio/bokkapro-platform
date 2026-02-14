"""add vehicle coordinates

Revision ID: 0003_add_vehicle_coordinates
Revises: 0002_add_vehicles_table
Create Date: 2026-02-14 00:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_add_vehicle_coordinates"
down_revision: Union[str, Sequence[str], None] = "0002_add_vehicles_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("vehicles", sa.Column("lat", sa.Float(), nullable=True))
    op.add_column("vehicles", sa.Column("lng", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("vehicles", "lng")
    op.drop_column("vehicles", "lat")
