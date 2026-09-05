"""
Pydantic Request & Response Schemas Boilerplate
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CaseBase(BaseModel):
    child_identifier: str
    referral_type: str

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: str
    status: str
    coordinator_id: Optional[str] = None
    current_bottleneck: Optional[str] = None
    created_date: datetime
    days_open: int = 0
    followup_attempts: int = 0

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: str
    bottleneck: str
    confidence: float
    recommended_action: str
    priority: str
    reason: str
    evidence_event_ids: List[str] = []
    requires_human_approval: bool = True
