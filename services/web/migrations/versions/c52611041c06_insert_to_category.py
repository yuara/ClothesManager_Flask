"""Insert to Category

Revision ID: c52611041c06
Revises: 1c5579d05a63
Create Date: 2020-06-22 22:37:09.162472

"""
from alembic import op
import sqlalchemy as sa
from project.models import Category


# revision identifiers, used by Alembic.
revision = "c52611041c06"
down_revision = "1c5579d05a63"
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(
        Category.__table__,
        [
            {
                "parent_id": 1,
                "child_id": 1,
                "parent_name": "tops",
                "child_name": "t-shirt",
            },
            {
                "parent_id": 1,
                "child_id": 2,
                "parent_name": "tops",
                "child_name": "shirt",
            },
            {
                "parent_id": 1,
                "child_id": 3,
                "parent_name": "tops",
                "child_name": "hoodie",
            },
            {
                "parent_id": 1,
                "child_id": 4,
                "parent_name": "tops",
                "child_name": "sweats",
            },
            {
                "parent_id": 2,
                "child_id": 5,
                "parent_name": "bottoms",
                "child_name": "pants",
            },
            {
                "parent_id": 2,
                "child_id": 6,
                "parent_name": "bottoms",
                "child_name": "shorts",
            },
            {
                "parent_id": 2,
                "child_id": 7,
                "parent_name": "bottoms",
                "child_name": "skirt",
            },
        ],
    )


def downgrade():
    op.drop_table("category")
    op.create_table(
        "category",
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("child_id", sa.Integer(), nullable=False),
        sa.Column("parent_name", sa.String(length=30), nullable=True),
        sa.Column("child_name", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("parent_id", "child_id"),
    )
