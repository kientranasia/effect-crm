"""Initial migration

Revision ID: 8a90e4832680
Revises: 
Create Date: 2025-04-17 18:39:17.689529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a90e4832680'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('outcome', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('follow_up_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('follow_up_notes', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interaction', schema=None) as batch_op:
        batch_op.drop_column('follow_up_notes')
        batch_op.drop_column('follow_up_date')
        batch_op.drop_column('outcome')
        batch_op.drop_column('notes')

    # ### end Alembic commands ###
