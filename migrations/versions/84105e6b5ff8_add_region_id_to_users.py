"""add region_id to users

Revision ID: 84105e6b5ff8
Revises: 3150a0123667
Create Date: 2024-XX-XX
"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic
revision: str = '84105e6b5ff8'
down_revision: Union[str, None] = '3150a0123667'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Создаем таблицу regions
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Создаем временную таблицу с новой структурой
    op.create_table(
        'users_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), unique=True, index=True),
        sa.Column('email', sa.String(100), unique=True, index=True),
        sa.Column('hashed_password', sa.String(200)),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('log_partner', sa.String(50)),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('regions.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Копируем данные из старой таблицы в новую
    op.execute('''
        INSERT INTO users_new (id, username, email, hashed_password, role, is_active, 
                             created_at, updated_at, log_partner)
        SELECT id, username, email, hashed_password, role, is_active, 
               created_at, updated_at, log_partner
        FROM users
    ''')

    # Удаляем старую таблицу
    op.drop_table('users')

    # Переименовываем новую таблицу
    op.rename_table('users_new', 'users')

    # Создаем индексы
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade():
    # При откате удаляем колонку region_id
    op.create_table(
        'users_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), unique=True, index=True),
        sa.Column('email', sa.String(100), unique=True, index=True),
        sa.Column('hashed_password', sa.String(200)),
        sa.Column('role', sa.String(10)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('log_partner', sa.String(50)),
        sa.PrimaryKeyConstraint('id')
    )

    op.execute('''
        INSERT INTO users_old (id, username, email, hashed_password, role, is_active, 
                             created_at, updated_at, log_partner)
        SELECT id, username, email, hashed_password, role, is_active, 
               created_at, updated_at, log_partner
        FROM users
    ''')

    op.drop_table('users')
    op.rename_table('users_old', 'users')
    op.drop_table('regions')

    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
