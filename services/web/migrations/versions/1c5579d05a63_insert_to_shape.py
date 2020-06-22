"""Insert to Shape

Revision ID: 1c5579d05a63
Revises: 9ce6ef1158da
Create Date: 2020-06-21 22:44:39.131991

"""
from alembic import op
import sqlalchemy as sa
from project.models import Shape


# revision identifiers, used by Alembic.
revision = "1c5579d05a63"
down_revision = "9ce6ef1158da"
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(
        Shape.__table__,
        [
            {"id": 1, "name": "tight"},
            {"id": 2, "name": "medium"},
            {"id": 3, "name": "wide"},
        ],
    )


def downgrade():
    op.drop_table("shape")
    op.create_table(
        "shape",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
