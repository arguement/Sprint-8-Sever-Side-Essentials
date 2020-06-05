"""empty message

Revision ID: d0e24f02b4f7
Revises: 
Create Date: 2020-06-04 18:54:31.611521

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd0e24f02b4f7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('category', sa.String(length=100), nullable=False))
    op.add_column('event', sa.Column('cost', sa.String(length=100), nullable=True))
    op.add_column('event', sa.Column('end_date', sa.DateTime(), nullable=False))
    op.add_column('event', sa.Column('flyer', sa.String(length=100), nullable=True))
    op.add_column('event', sa.Column('name', sa.String(length=100), nullable=False))
    op.add_column('event', sa.Column('start_date', sa.DateTime(), nullable=False))
    op.add_column('event', sa.Column('venue', sa.String(length=100), nullable=True))
    op.drop_column('event', 'event_date')
    op.add_column('user', sa.Column('visbility', sa.Boolean(), nullable=True))
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=140),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=140),
               nullable=False)
    op.drop_column('user', 'visbility')
    op.add_column('event', sa.Column('event_date', mysql.DATETIME(), nullable=True))
    op.drop_column('event', 'venue')
    op.drop_column('event', 'start_date')
    op.drop_column('event', 'name')
    op.drop_column('event', 'flyer')
    op.drop_column('event', 'end_date')
    op.drop_column('event', 'cost')
    op.drop_column('event', 'category')
    # ### end Alembic commands ###
