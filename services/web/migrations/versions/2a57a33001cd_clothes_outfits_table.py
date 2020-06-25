"""clothes_outfits table

Revision ID: 2a57a33001cd
Revises: 230b4263d8eb
Create Date: 2020-06-24 21:39:33.264431

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a57a33001cd"
down_revision = "230b4263d8eb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "clothes_outfits",
        sa.Column("clothes_id", sa.Integer(), nullable=True),
        sa.Column("outfit_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["clothes_id"], ["clothes.id"],),
        sa.ForeignKeyConstraint(["outfit_id"], ["outfit.id"],),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("clothes_outfits")
    # ### end Alembic commands ###
