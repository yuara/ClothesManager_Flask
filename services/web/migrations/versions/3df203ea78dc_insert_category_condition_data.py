"""Insert category condition data

Revision ID: 3df203ea78dc
Revises: cc13435e45f1
Create Date: 2020-07-15 17:59:33.716940

"""
from alembic import op
import sqlalchemy as sa
import json
from pathlib import Path
from project.models import category_condition


# revision identifiers, used by Alembic.
revision = "3df203ea78dc"
down_revision = "cc13435e45f1"
branch_labels = None
depends_on = None


def upgrade():
    current_dir = Path(__file__)
    datasets_dir = current_dir.parents[1] / "data"
    file_name = datasets_dir.joinpath("category_condition.json")

    with file_name.open() as f:
        df = json.load(f)

    op.bulk_insert(category_condition, df)


def downgrade():
    op.drop_table("category_condition")

    op.create_table(
        "category_condition",
        sa.Column("clothes_index_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"],),
        sa.ForeignKeyConstraint(["clothes_index_id"], ["clothes_index.id"],),
    )
