"""add region_id to users

Revision ID: add_region_id_to_users
Revises: previous_revision_id
Create Date: 2024-XX-XX

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_region_id_to_users'
down_revision = 'previous_revision_id'  # Укажите ID предыдущей миграции
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем колонку region_id в таблицу users
    op.add_column('users', sa.Column('region_id', sa.String(50), nullable=True))

def downgrade():
    # Удаляем колонку при откате
    op.drop_column('users', 'region_id') 