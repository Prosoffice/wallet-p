"""empty message

Revision ID: ad52824ff647
Revises: ce022c3e29bd
Create Date: 2021-05-03 03:01:54.411634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad52824ff647'
down_revision = 'ce022c3e29bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'user_roles', ['id'])
    op.create_unique_constraint(None, 'users', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'user_roles', type_='unique')
    # ### end Alembic commands ###
