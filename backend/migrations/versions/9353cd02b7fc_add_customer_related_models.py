"""Add Customer related models

Revision ID: 9353cd02b7fc
Revises: 1ec08862d786
Create Date: 2023-07-26 23:58:03.843542

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9353cd02b7fc"
down_revision = "1ec08862d786"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customerCode", sa.String(length=11), nullable=False),
        sa.Column("parentCustomerCode", sa.String(length=11), nullable=True),
        sa.Column("customerName", sa.String(length=50), nullable=False),
        sa.Column("contactLastName", sa.String(length=50), nullable=True),
        sa.Column("contactFirstName", sa.String(length=50), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("addressLine1", sa.String(length=1024), nullable=True),
        sa.Column("addressLine2", sa.String(length=1024), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=True),
        sa.Column("postalCode", sa.String(length=15), nullable=True),
        sa.Column("country", sa.String(length=50), nullable=True),
        sa.Column("customerType", sa.String(length=50), nullable=True),
        sa.Column("logoFile", sa.String(length=64), nullable=True),
        sa.Column("createdAt", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "customers_meta",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clientName", sa.String(length=255), nullable=True),
        sa.Column("customerCode", sa.String(length=11), nullable=False),
        sa.Column("customerMetaGraylogIndex", sa.String(length=1024), nullable=True),
        sa.Column("customerMetaGraylogStream", sa.String(length=1024), nullable=True),
        sa.Column("customerMetaInfluxOrg", sa.String(length=1024), nullable=True),
        sa.Column("customerMetaGrafanaOrg", sa.String(length=1024), nullable=True),
        sa.Column("customerMetaWazuhGroup", sa.String(length=1024), nullable=True),
        sa.Column("indexRetention", sa.Integer(), nullable=True),
        sa.Column("wazuhRegistrationPort", sa.Integer(), nullable=True),
        sa.Column("wazuhLogIngestionPort", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("customers_meta")
    op.drop_table("customers")
    # ### end Alembic commands ###
