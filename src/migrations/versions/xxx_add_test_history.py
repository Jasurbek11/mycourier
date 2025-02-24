"""add test history data

Revision ID: xxx
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # Добавляем тестовые записи в историю
    op.execute("""
        INSERT INTO courier_history (
            courier_id, type, event, created_at, created_by_id
        ) VALUES 
        (1, 'onboarding', 'Начало оформления', NOW(), 1),
        (1, 'onboarding', 'Загружены документы', NOW(), 1),
        (1, 'onboarding', 'Проверка документов', NOW(), 1),
        (1, 'onboarding', 'Оформление завершено', NOW(), 1),
        
        (1, 'activation', 'Активация аккаунта', NOW(), 1),
        (1, 'activation', 'Деактивация аккаунта', NOW(), 1),
        
        (1, 'service', 'Начало работы', NOW(), 1),
        (1, 'service', 'Бонус за друга', NOW(), 1),
        
        (1, 'warehouse', 'Выдан телефон', NOW(), 1),
        (1, 'warehouse', 'Возврат телефона', NOW(), 1),
        
        (1, 'payment', 'Начисление выплаты', NOW(), 1),
        (1, 'payment', 'Выплата произведена', NOW(), 1)
    """)

def downgrade():
    op.execute("DELETE FROM courier_history") 