from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
"""
SQLAlchemy models → Database

Pydantic models → Data being passed around
"""

class Account(BaseModel):
    account_id: UUID
    transaction_count: int
    average_amount: Decimal | None
    latest_transaction_at: datetime | None


class MerchantRiskEvidence(BaseModel):
    merchant: str
    merchant_category: str
    historical_fraud_rate: Decimal | None



class DeviceLocationEvidence(BaseModel):
    device_seen_before: bool
    country_seen_before: bool | None



class PriorDisputeEvidence(BaseModel):
    dispute_count: int
    most_recent_dispute: datetime | None

    