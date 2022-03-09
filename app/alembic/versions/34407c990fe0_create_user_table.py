"""create user table

Revision ID: 34407c990fe0
Revises: 6b221c6eff2e
Create Date: 2022-03-06 20:50:47.103125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34407c990fe0'
down_revision = '6b221c6eff2e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
    )


def downgrade():
    op.drop_table('users')
