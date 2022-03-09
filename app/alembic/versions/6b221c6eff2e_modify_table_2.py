"""modify table 2

Revision ID: 6b221c6eff2e
Revises: e9697f9e58a5
Create Date: 2022-03-05 16:47:21.193078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b221c6eff2e'
down_revision = 'e9697f9e58a5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('notes', sa.Column('text2', sa.String(), nullable=True))


def downgrade():
    op.drop_column('notes', 'text2')
