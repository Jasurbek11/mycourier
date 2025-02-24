"""update status values

Revision ID: xxx
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op

def upgrade():
    # Обновляем статусы документов
    op.execute("UPDATE couriers SET documents_status = 'NOT_VERIFIED' WHERE documents_status = 'PENDING'")
    op.execute("UPDATE couriers SET documents_status = 'VERIFIED' WHERE documents_status = 'APPROVED'")
    op.execute("UPDATE couriers SET documents_status = 'PROBLEM' WHERE documents_status = 'REJECTED'")
    
    # Обновляем статусы документов на транспорт
    op.execute("UPDATE couriers SET vehicle_docs_status = 'NOT_VERIFIED' WHERE vehicle_docs_status = 'PENDING'")
    op.execute("UPDATE couriers SET vehicle_docs_status = 'VERIFIED' WHERE vehicle_docs_status = 'APPROVED'")
    op.execute("UPDATE couriers SET vehicle_docs_status = 'PROBLEM' WHERE vehicle_docs_status = 'REJECTED'")

def downgrade():
    # Возвращаем старые значения
    op.execute("UPDATE couriers SET documents_status = 'PENDING' WHERE documents_status = 'NOT_VERIFIED'")
    op.execute("UPDATE couriers SET documents_status = 'APPROVED' WHERE documents_status = 'VERIFIED'")
    op.execute("UPDATE couriers SET documents_status = 'REJECTED' WHERE documents_status = 'PROBLEM'")
    
    op.execute("UPDATE couriers SET vehicle_docs_status = 'PENDING' WHERE vehicle_docs_status = 'NOT_VERIFIED'")
    op.execute("UPDATE couriers SET vehicle_docs_status = 'APPROVED' WHERE vehicle_docs_status = 'VERIFIED'")
    op.execute("UPDATE couriers SET vehicle_docs_status = 'REJECTED' WHERE vehicle_docs_status = 'PROBLEM'") 