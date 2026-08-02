import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

#enum -> Unique and Immutable: so we can do current_enum = FlagStatus.UNFLAGGED -> current_enum.name = unflagged 

class FlagStatus(str, enum.Enum): #Represents the lifecycle of a transaction flag
    UNFLAGGED = "unflagged"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DecisionType(str, enum.Enum): #LLM's actual conclusion
    CLEAR = "clear"
    ESCALATE = "escalate"
    NEED_MORE_DATA = "need_more_data"


class ReviewStatus(str, enum.Enum): #Human Review
    QUEUED = "queued"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"



class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Mapped[] Python type hinting, mapped_column() -> Create the database column with these rules
    external_reference: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    profile: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)



class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (Index("ix_transactions_flag_status", "flag_status"),) #creates an index that sorts flag_status

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CAD")
    merchant: Mapped[str] = mapped_column(String(160), nullable=False)
    merchant_category: Mapped[str] = mapped_column(String(80), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    payment_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    device_fingerprint: Mapped[str | None] = mapped_column(String(128))
    ip_country: Mapped[str | None] = mapped_column(String(2))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    flag_status: Mapped[FlagStatus] = mapped_column(Enum(FlagStatus, name="flag_status"), nullable=False, default=FlagStatus.UNFLAGGED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    account: Mapped[Account] = relationship() #allow for transaction.account which tells SQLAlchemy to find the Account whose id matches this transaction's account_id (Python object connection)
    investigation_runs: Mapped[list["InvestigationRun"]] = relationship(back_populates="transaction") #This creates a two-way relationship -> transactions.investigation_runs & investigations_runs.transaction works



class DeviceEvent(Base):
    __tablename__ = "device_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    device_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    ip_country: Mapped[str | None] = mapped_column(String(2))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)



class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True) #deletes all accounts with the same accounts.id in child tables
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"), index=True) #doesnt remove the transactions just sets those rows to NULL
    reason: Mapped[str] = mapped_column(String(120), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    filed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)



class InvestigationRun(Base):
    __tablename__ = "investigation_runs"
    __table_args__ = (Index("ix_investigation_runs_transaction_id", "transaction_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=False) # ondelete=RESTRICT prevents the deletion of a parent record if any child records are still linked to it
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus, name="run_status"), nullable=False, default=RunStatus.PENDING)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model_version: Mapped[str] = mapped_column(String(120), nullable=False)
    threshold_version: Mapped[str | None] = mapped_column(String(64))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transaction: Mapped[Transaction] = relationship(back_populates="investigation_runs")
    evidence_snapshots: Mapped[list["EvidenceSnapshot"]] = relationship(back_populates="run") #Which InvestigationRun does this snapshot belong to?
    trace_events: Mapped[list["DecisionTraceEvent"]] = relationship(back_populates="run")
    decision: Mapped["AgentDecision | None"] = relationship(back_populates="run")

    """ evidence_snapshots gives you 
    [
        EvidenceSnapshot(id=1),
        EvidenceSnapshot(id=2),
        EvidenceSnapshot(id=3)
    ]
    """


class EvidenceSnapshot(Base):
    __tablename__ = "evidence_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investigation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    run: Mapped[InvestigationRun] = relationship(back_populates="evidence_snapshots") #What evidence snapshots belong to this run shows a list of 
    """
    run gives you 
        InvestigationRun(
        id=1,
        status="completed"
    )
    """



class DecisionTraceEvent(Base):
    __tablename__ = "decision_trace_events"
    __table_args__ = (UniqueConstraint("investigation_run_id", "sequence", name="uq_trace_event_run_sequence"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investigation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(48), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    run: Mapped[InvestigationRun] = relationship(back_populates="trace_events")



class AgentDecision(Base):
    __tablename__ = "agent_decisions"
    __table_args__ = (
        Index("ix_agent_decisions_decision", "decision"),
        Index("ix_agent_decisions_confidence", "confidence"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("investigation_runs.id", ondelete="RESTRICT"), nullable=False, unique=True)
    decision: Mapped[DecisionType] = mapped_column(Enum(DecisionType, name="decision_type"), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    model_version: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    run: Mapped[InvestigationRun] = relationship(back_populates="decision")



class ReviewCase(Base):
    __tablename__ = "review_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_decision_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_decisions.id", ondelete="RESTRICT"), nullable=False, unique=True)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus, name="review_status"), nullable=False, default=ReviewStatus.QUEUED)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))



class HumanOverride(Base):
    __tablename__ = "human_overrides"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_decision_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_decisions.id", ondelete="RESTRICT"), nullable=False, index=True)
    human_decision: Mapped[DecisionType] = mapped_column(Enum(DecisionType, name="human_decision_type"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)