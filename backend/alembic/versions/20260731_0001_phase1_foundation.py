"""create phase 1 foundation schema

Revision ID: 20260731_0001
Revises:
Create Date: 2026-07-31
"""

from alembic import op #Alembic gives you this object to modify the database. (e.g op.create_table, op.execute, op.drop_table)

from app.db.base import Base
from app.db import models

revision = "20260731_0001"
down_revision = None #this is the the first migration
branch_labels = None
depends_on = None 

def upgrade() -> None:
    connection = op.get_bind()
    Base.metadata.create_all(connection)

    # The operational app role can access only the public operational schema.
    op.execute("DO $$ BEGIN EXECUTE format('REVOKE ALL ON DATABASE %I FROM PUBLIC', current_database()); END $$")
    op.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA public TO trustline_app, trustline_evaluator")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO trustline_app")
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO trustline_app")
    op.execute("GRANT SELECT ON transactions TO trustline_evaluator")
    op.execute("GRANT REFERENCES (id) ON transactions TO trustline_evaluator")
    op.execute("DO $$ BEGIN EXECUTE format('GRANT CONNECT ON DATABASE %I TO trustline_app, trustline_evaluator', current_database()); END $$")

    # Ground truth is deliberately outside application metadata and ownership.
    op.execute("CREATE SCHEMA evaluation AUTHORIZATION trustline_evaluator")
    op.execute("REVOKE ALL ON SCHEMA evaluation FROM PUBLIC")
    op.execute("SET ROLE trustline_evaluator")
    op.execute(
        """
        CREATE TABLE evaluation.transaction_ground_truth (
            transaction_id UUID PRIMARY KEY REFERENCES public.transactions(id) ON DELETE CASCADE,
            ground_truth_label VARCHAR(32) NOT NULL,
            labeled_at TIMESTAMPTZ NOT NULL
        )
        """
    )
    op.execute("RESET ROLE")


def downgrade() -> None:
    connection = op.get_bind()
    op.execute("DROP SCHEMA IF EXISTS evaluation CASCADE")
    Base.metadata.drop_all(connection)
