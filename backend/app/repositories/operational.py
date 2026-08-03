"""The only model registry future evidence repositories may use."""

from app.db.models import Account, DeviceEvent, Dispute, Transaction #These are the four operational models that an evidence tool is allowed to use.

EVIDENCE_SOURCE_MODELS = (Account, Transaction, DeviceEvent, Dispute)