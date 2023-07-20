"""initial migration

Revision ID: 985a0c8b7893
Revises: 
Create Date: 2023-07-20 10:33:16.408621

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "985a0c8b7893"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("tg_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("full_name", sa.String(length=50), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("tg_id"),
    )
    op.create_table(
        "orders",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("fk_tg_id", sa.Integer(), nullable=False),
        sa.Column("urls", sa.Text(), nullable=False),
        sa.Column("count_urls", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["fk_tg_id"],
            ["users.tg_id"],
        ),
        sa.PrimaryKeyConstraint("order_id"),
    )
    op.create_table(
        "transactions",
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("fk_tg_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.String(length=128), nullable=False),
        sa.Column("amount", sa.DECIMAL(precision=16, scale=4), nullable=True),
        sa.Column("amount_points", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["fk_tg_id"],
            ["users.tg_id"],
        ),
        sa.PrimaryKeyConstraint("transaction_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("transactions")
    op.drop_table("orders")
    op.drop_table("users")
    # ### end Alembic commands ###