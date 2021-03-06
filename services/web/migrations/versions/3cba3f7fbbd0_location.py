"""Location

Revision ID: 3cba3f7fbbd0
Revises: 6eaf3618c364
Create Date: 2020-07-07 09:13:54.307511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3cba3f7fbbd0"
down_revision = "d6cff2f1e846"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_location_id"), table_name="user")
    op.drop_column("user", "location_id")
    op.drop_table("location")
    # ### end Alembic commands ###
