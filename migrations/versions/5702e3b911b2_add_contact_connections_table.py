"""Add contact connections table

Revision ID: 5702e3b911b2
Revises: e93dd1a5ef27
Create Date: 2024-03-27 16:42:42.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '5702e3b911b2'
down_revision = 'e93dd1a5ef27'
branch_labels = None
depends_on = None


def upgrade():
    # Create contact_connections table
    op.create_table('contact_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('connected_contact_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name='fk_contact_connections_contact_id'),
        sa.ForeignKeyConstraint(['connected_contact_id'], ['contacts.id'], name='fk_contact_connections_connected_contact_id'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_contact_connections_created_by_id'),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], name='fk_contact_connections_updated_by_id'),
        sa.PrimaryKeyConstraint('id')
    )

    # Drop contact_id from projects table
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('contact_id')

    with op.batch_alter_table('contacts', schema=None) as batch_op:
        batch_op.alter_column('interests',
               existing_type=sa.TEXT(),
               type_=sa.String(length=500),
               existing_nullable=True)
        batch_op.alter_column('probability',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('expected_close_date',
               existing_type=sa.DATETIME(),
               type_=sa.Date(),
               existing_nullable=True)

    with op.batch_alter_table('interactions', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=50),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # Add back contact_id to projects table
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contact_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_projects_contact_id', 'contacts', ['contact_id'], ['id'])

    with op.batch_alter_table('interactions', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    with op.batch_alter_table('contacts', schema=None) as batch_op:
        batch_op.alter_column('expected_close_date',
               existing_type=sa.Date(),
               type_=sa.DATETIME(),
               existing_nullable=True)
        batch_op.alter_column('probability',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)
        batch_op.alter_column('interests',
               existing_type=sa.String(length=500),
               type_=sa.TEXT(),
               existing_nullable=True)

    # Drop contact_connections table
    op.drop_table('contact_connections')
    # ### end Alembic commands ###
