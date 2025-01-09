"""Distinguish virtual and in_person events. Add google maps locations/places to events. new Locations table.

Revision ID: ff3237bdb44f
Revises: 087dfed202cf
Create Date: 2025-01-09 13:33:33.247991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff3237bdb44f'
down_revision = '087dfed202cf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('place_id', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('place_id')
    )
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('event_type', sa.String(length=40), nullable=True))
        batch_op.create_foreign_key('fk_event_location_id', 'locations', ['location_id'], ['id'])
        batch_op.drop_column('location')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', sa.VARCHAR(length=80), nullable=False))
        batch_op.drop_constraint('fk_event_location_id', type_='foreignkey')
        batch_op.drop_column('event_type')
        batch_op.drop_column('location_id')

    op.drop_table('locations')
    # ### end Alembic commands ###
