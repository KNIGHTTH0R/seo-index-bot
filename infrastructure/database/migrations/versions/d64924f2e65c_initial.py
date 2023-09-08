"""initial

Revision ID: d64924f2e65c
Revises: 105b336296d6
Create Date: 2023-09-03 11:07:26.688695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd64924f2e65c'
down_revision = '105b336296d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'count_urls',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'count_urls',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###