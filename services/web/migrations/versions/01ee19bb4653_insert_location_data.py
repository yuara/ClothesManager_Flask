"""Insert location data

Revision ID: 01ee19bb4653
Revises: 3cba3f7fbbd0
Create Date: 2020-07-07 09:14:23.401334

"""
from alembic import op
import sqlalchemy as sa
import json
from pathlib import Path
from project.models import Location


# revision identifiers, used by Alembic.
revision = "01ee19bb4653"
down_revision = "3cba3f7fbbd0"
branch_labels = None
depends_on = None


def upgrade():
    current_dir = Path(__file__)
    datasets_dir = current_dir.parents[1] / "data"
    file_name = datasets_dir.joinpath("location.json")

    with file_name.open() as f:
        df = json.load(f)

    op.bulk_insert(Location.__table__, df)


def downgrade():
    op.drop_index(op.f("ix_user_location_id"), table_name="user")
    op.drop_column("user", "location_id")
    op.drop_table("location")

    op.create_table(
        "location",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=True),
        sa.Column("pref_id", sa.Integer(), nullable=True),
        sa.Column("city_id", sa.Integer(), nullable=True),
        sa.Column("area_name", sa.String(length=20), nullable=True),
        sa.Column("pref_name", sa.String(length=20), nullable=True),
        sa.Column("city_name", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("user", sa.Column("location_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_user_location_id"), "user", ["location_id"], unique=False)
