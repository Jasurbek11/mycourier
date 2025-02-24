"""create regions and add region_id

Revision ID: create_regions_and_add_region_id
Revises: 3150a0123667
Create Date: 2024-02-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'create_regions_and_add_region_id'
down_revision = '3150a0123667'  # ID начальной миграции
branch_labels = None
depends_on = None

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

    # Добавляем колонку region_id в таблицу users
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('region_id', sa.Integer(), nullable=True))

def downgrade():
    # Удаляем колонку region_id из таблицы users
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('region_id')
    
    # Удаляем таблицу regions
    op.drop_table('regions') 