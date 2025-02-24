"""add region_id to users

Revision ID: add_region_id_to_users
Revises: xxxx
Create Date: 2024-02-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_region_id_to_users'
down_revision = 'xxxx'  # Укажите ID предыдущей миграции
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем колонку region_id в таблицу users
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('region_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_users_region',
            'regions',
            ['region_id'],
            ['id']
        )

def downgrade():
    # Удаляем колонку при откате
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('fk_users_region', type_='foreignkey')
        batch_op.drop_column('region_id') 