"""empty message

Revision ID: 97dee9d0c307
Revises: f6d0391aa014
Create Date: 2021-05-01 09:18:44.917005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97dee9d0c307'
down_revision = 'f6d0391aa014'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'user_roles', ['id'])
    op.create_unique_constraint(None, 'users', ['id'])
    op.add_column('wallet', sa.Column('wallet_id', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'wallet', ['wallet_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='unique')
    op.drop_column('wallet', 'wallet_id')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'user_roles', type_='unique')
    # ### end Alembic commands ###