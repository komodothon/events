"""Add image_path column to Event model

Revision ID: 087dfed202cf
Revises: d86e362c6b90
Create Date: 2025-01-06 13:51:04.790734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '087dfed202cf'
down_revision = 'd86e362c6b90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_path', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_column('image_path')

    # ### end Alembic commands ###
