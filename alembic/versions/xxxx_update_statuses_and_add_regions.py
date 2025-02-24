"""update statuses and add regions

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-02-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'xxxx'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем таблицу регионов
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
        batch_op.create_foreign_key('fk_users_region', 'regions', ['region_id'], ['id'])

    # Обновляем статусы онбординга
    # В SQLite мы просто обновляем значения в строках
    op.execute("UPDATE couriers SET onboarding_status = 'WILL_BE_VERIFIED' WHERE onboarding_status = 'IN_PROGRESS'")

def downgrade():
    # Возвращаем статусы обратно
    op.execute("UPDATE couriers SET onboarding_status = 'IN_PROGRESS' WHERE onboarding_status = 'WILL_BE_VERIFIED'")
    
    # Удаляем foreign key и колонку region_id
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('fk_users_region', type_='foreignkey')
        batch_op.drop_column('region_id')
    
    # Удаляем таблицу регионов
    op.drop_table('regions') 