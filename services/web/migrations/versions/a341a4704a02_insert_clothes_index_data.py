"""Insert clothes index data

Revision ID: a341a4704a02
Revises: 89f21945899b
Create Date: 2020-07-10 11:32:55.879310

"""
from alembic import op
import sqlalchemy as sa
import json
from pathlib import Path
from project.models import ClothesIndex


# revision identifiers, used by Alembic.
revision = "a341a4704a02"
down_revision = "89f21945899b"
branch_labels = None
depends_on = None


def upgrade():
    current_dir = Path(__file__)
    datasets_dir = current_dir.parents[1] / "data"
    file_name = datasets_dir.joinpath("clothes_index.json")

    with file_name.open() as f:
        df = json.load(f)

    op.bulk_insert(ClothesIndex.__table__, df)


def downgrade():
    op.drop_table("clothes_index")

    op.create_table(
        "clothes_index",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=140), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
