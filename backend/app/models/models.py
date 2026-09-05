import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from .database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    child_identifier = Column(String, nullable=False)
    referral_type = Column(String, nullable=False)
    status = Column(String, default="NEW", nullable=False)
    coordinator_id = Column(String, nullable=True)
    current_bottleneck = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    followup_attempts = Column(Integer, default=0, nullable=False)


class CaseEvent(Base):
    __tablename__ = "case_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    event_type = Column(String, nullable=False)
    details = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class Specialist(Base):
    __tablename__ = "specialists"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    availability_status = Column(String, default="AVAILABLE", nullable=False)
    active = Column(Boolean, default=True, nullable=False)
