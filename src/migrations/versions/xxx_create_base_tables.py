"""create base tables

Revision ID: xxx
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'create_base_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Создаем таблицу users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('log_partner', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Создаем таблицу couriers
    op.create_table(
        'couriers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('pinfl', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('onboarding_status', sa.String(), nullable=False),
        sa.Column('documents_status', sa.String(), nullable=False),
        sa.Column('transport_type', sa.String(), nullable=False),
        sa.Column('vehicle_number', sa.String(), nullable=True),
        sa.Column('vehicle_model', sa.String(), nullable=True),
        sa.Column('vehicle_docs_status', sa.String(), nullable=True),
        sa.Column('log_partner', sa.String(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('verified_by_id', sa.Integer(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
        sa.UniqueConstraint('pinfl')
    )

    # Создаем таблицу courier_history
    op.create_table(
        'courier_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('event', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('documents_status', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('equipment_name', sa.String(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('courier_history')
    op.drop_table('couriers')
    op.drop_table('users') 