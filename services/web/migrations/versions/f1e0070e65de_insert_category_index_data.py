"""Insert category index data

Revision ID: f1e0070e65de
Revises: fcb227d82bdd
Create Date: 2020-07-15 11:04:12.980878

"""
from alembic import op
import sqlalchemy as sa
import json
from pathlib import Path
from project.models import category_index


# revision identifiers, used by Alembic.
revision = "f1e0070e65de"
down_revision = "fcb227d82bdd"
branch_labels = None
depends_on = None


def upgrade():
    current_dir = Path(__file__)
    datasets_dir = current_dir.parents[1] / "data"
    file_name = datasets_dir.joinpath("category_index.json")

    with file_name.open() as f:
        df = json.load(f)

    op.bulk_insert(category_index, df)


def downgrade():
    op.drop_table("category_index")

    op.create_table(
        "category_index",
        sa.Column("clothes_index_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("conditional", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"],),
        sa.ForeignKeyConstraint(["clothes_index_id"], ["clothes_index.id"],),
    )
