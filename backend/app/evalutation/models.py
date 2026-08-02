"""Evaluator-only models.

This module must never be imported by app.repositories or future evidence tools.
The runtime application role is denied schema access at the database level.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class EvaluationBase(DeclarativeBase):
    pass


class TransactionGroundTruth(EvaluationBase):
    __tablename__ = "transaction_ground_truth"
    __table_args__ = {"schema": "evaluation"} #Put this table inside the evaluation folder instead of the default public folder where all other tables are

    transaction_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    ground_truth_label: Mapped[str] = mapped_column(String(32), nullable=False)
    labeled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    