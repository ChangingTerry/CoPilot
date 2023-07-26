"""Add Users related models

Revision ID: 09189f03c3ee
Revises: 9353cd02b7fc
Create Date: 2023-07-27 00:14:11.238239

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "09189f03c3ee"
down_revision = "9353cd02b7fc"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customerCode", sa.String(length=11), nullable=False),
        sa.Column("usersFirstName", sa.String(length=50), nullable=True),
        sa.Column("usersLastName", sa.String(length=50), nullable=True),
        sa.Column("usersEmail", sa.String(length=50), nullable=True),
        sa.Column("usersRole", sa.String(length=100), nullable=True),
        sa.Column("imageFile", sa.String(length=64), nullable=True),
        sa.Column("notifications", sa.SmallInteger(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    # ### end Alembic commands ###
