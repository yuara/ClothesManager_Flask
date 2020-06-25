"""Insert category data

Revision ID: 908e6ac8c23b
Revises: 29ca91eedb9a
Create Date: 2020-06-25 15:38:42.672477

"""
from alembic import op
import sqlalchemy as sa
import json
from pathlib import Path
from project.models import Category


# revision identifiers, used by Alembic.
revision = "908e6ac8c23b"
down_revision = "29ca91eedb9a"
branch_labels = None
depends_on = None


def upgrade():
    current_dir = Path(__file__)
    datasets_dir = current_dir.parents[1] / "data"
    file_name = datasets_dir.joinpath("category.json")

    with file_name.open() as f:
        df = json.load(f)

    op.bulk_insert(Category.__table__, df)


def downgrade():
    op.drop_index(op.f("ix_category_parent_id"), table_name="category")
    op.drop_index(op.f("ix_category_child_id"), table_name="category")
    op.drop_table("category")

    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("child_id", sa.Integer(), nullable=True),
        sa.Column("parent_name", sa.String(length=30), nullable=True),
        sa.Column("child_name", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_category_child_id"), "category", ["child_id"], unique=False
    )
    op.create_index(
        op.f("ix_category_parent_id"), "category", ["parent_id"], unique=False
    )
