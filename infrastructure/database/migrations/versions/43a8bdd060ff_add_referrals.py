"""add referrals

Revision ID: 43a8bdd060ff
Revises: d64924f2e65c
Create Date: 2023-09-07 13:20:13.364054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43a8bdd060ff'
down_revision = 'd64924f2e65c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('referrer_id', sa.BIGINT(), nullable=True))
    op.create_foreign_key(None, 'users', 'users', ['referrer_id'], ['tg_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'referrer_id')
    # ### end Alembic commands ###