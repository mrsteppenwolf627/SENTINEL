"""
SQLAlchemy ORM models for the Sentinel persistence layer.

These are internal implementation details of the infrastructure layer.
External code (core, modules) must never import from this file directly;
all communication goes through the Repository interfaces.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Enum as SQLEnum

from app.core.entities import ActionType, AlertSeverity, RiskLevel


class Base(DeclarativeBase):
    """Shared declarative base for all Sentinel ORM models."""
    pass


class IncidentModel(Base):
    """
    Represents an ongoing or historical incident derived from an alert.
    Lifecycle: OPEN → ANALYZING → MITIGATING → CLOSED
    """
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(36), nullable=False, index=True)
    status = Column(String, default="OPEN", index=True)
    source = Column(String, nullable=False, index=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    message = Column(String, nullable=False)
    metadata_json = Column(JSONB, default=dict)
    enriched_context = Column(JSONB, default=dict)
    rca_hypothesis = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)

    plans = relationship(
        "RemediationPlanModel",
        back_populates="incident",
        cascade="all, delete-orphan",
    )


class RemediationPlanModel(Base):
    """Represents an actionable remediation plan attached to an incident."""
    __tablename__ = "remediation_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Flattened Diagnosis fields (avoids a separate table for now)
    diagnosis_root_cause = Column(String, nullable=False)
    diagnosis_confidence = Column(Float, nullable=False)

    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    requires_approval = Column(Boolean, default=False)
    status = Column(String, default="PENDING", index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    incident = relationship("IncidentModel", back_populates="plans")


class AuditLogModel(Base):
    """
    WORM (Write-Once-Read-Many) audit log table.
    Records every significant event in the Sentinel pipeline.
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    component = Column(String, nullable=False, index=True)
    event = Column(String, nullable=False, index=True)
    details = Column(JSONB, nullable=False)
