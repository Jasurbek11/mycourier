"""update document status enum

Revision ID: xxx
Revises: create_base_tables
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_document_status'
down_revision = 'create_base_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Для SQLite мы просто обновляем значения в существующих столбцах
    op.execute("UPDATE couriers SET documents_status = 'PROBLEM' WHERE documents_status = 'NOT_VERIFIED'")
    op.execute("UPDATE couriers SET documents_status = 'OK' WHERE documents_status = 'VERIFIED'")
    op.execute("UPDATE couriers SET documents_status = 'PROBLEM' WHERE documents_status IN ('REJECTED_BY_COURIER', 'REJECTED_BY_HUB')")
    
    op.execute("UPDATE couriers SET vehicle_docs_status = 'PROBLEM' WHERE vehicle_docs_status = 'NOT_VERIFIED'")
    op.execute("UPDATE couriers SET vehicle_docs_status = 'OK' WHERE vehicle_docs_status = 'VERIFIED'")
    op.execute("UPDATE couriers SET vehicle_docs_status = 'PROBLEM' WHERE vehicle_docs_status IN ('REJECTED_BY_COURIER', 'REJECTED_BY_HUB')")

def downgrade():
    # Откатываем изменения
    op.execute("UPDATE couriers SET documents_status = 'NOT_VERIFIED' WHERE documents_status = 'PROBLEM'")
    op.execute("UPDATE couriers SET documents_status = 'VERIFIED' WHERE documents_status = 'OK'")
    
    op.execute("UPDATE couriers SET vehicle_docs_status = 'NOT_VERIFIED' WHERE vehicle_docs_status = 'PROBLEM'")
    op.execute("UPDATE couriers SET vehicle_docs_status = 'VERIFIED' WHERE vehicle_docs_status = 'OK'") 