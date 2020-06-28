"""Insert shape data

Revision ID: deff69599b25
Revises: c1a266b4e967
Create Date: 2020-06-25 15:35:19.810952

"""
from alembic import op
import sqlalchemy as sa
import json
from pathlib import Path
from project.models import Shape

# revision identifiers, used by Alembic.
revision = "deff69599b25"
down_revision = "c1a266b4e967"
branch_labels = None
depends_on = None


def upgrade():
    current_dir = Path(__file__)
    datasets_dir = current_dir.parents[1] / "data"
    file_name = datasets_dir.joinpath("shape.json")

    with file_name.open() as f:
        df = json.load(f)

    op.bulk_insert(Shape.__table__, df)


def downgrade():
    op.drop_table("shape")

    op.create_table(
        "shape",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
