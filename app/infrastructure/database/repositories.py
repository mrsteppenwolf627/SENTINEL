"""
Repository implementations for the Sentinel persistence layer.

DESIGN RULE (Correction 2):
All repositories accept and return Pydantic domain entities from app.core.entities.
The translation between Pydantic entity ↔ SQLAlchemy model happens EXCLUSIVELY
inside each repository method. External callers never import or touch SQLAlchemy models.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities import AuditLog, Incident, RemediationPlan
from app.infrastructure.database.models import (
    AuditLogModel,
    IncidentModel,
    RemediationPlanModel,
)


class IncidentRepository:
    """Persists and retrieves Incident domain entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, incident: Incident) -> Incident:
        """
        Persist a new Incident entity.

        Translates the Pydantic entity to an ORM model internally,
        then returns the original entity (not the model).
        """
        db_model = IncidentModel(
            id=incident.id,
            alert_id=incident.alert_id,
            source=incident.source,
            severity=incident.severity,
            message=incident.message,
            metadata_json=incident.metadata,
            status=incident.status,
            created_at=incident.created_at,
            closed_at=incident.closed_at,
        )
        self.session.add(db_model)
        await self.session.flush()
        return incident

    async def get_by_id(self, incident_id: str) -> Optional[Incident]:
        """Retrieve an Incident entity by its ID, or None if not found."""
        result = await self.session.execute(
            select(IncidentModel).where(IncidentModel.id == incident_id)
        )
        db_model: Optional[IncidentModel] = result.scalars().first()
        if db_model is None:
            return None
        return Incident(
            id=db_model.id,
            alert_id=db_model.alert_id,
            source=db_model.source,
            severity=db_model.severity,
            message=db_model.message,
            metadata=db_model.metadata_json or {},
            status=db_model.status,
            created_at=db_model.created_at,
            closed_at=db_model.closed_at,
        )


class PlanRepository:
    """Persists and retrieves RemediationPlan domain entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, plan: RemediationPlan, incident_id: str) -> RemediationPlan:
        """
        Persist a new RemediationPlan entity linked to the given incident_id.

        The Diagnosis is flattened into the plan model columns.
        Returns the original Pydantic entity.
        """
        db_model = RemediationPlanModel(
            id=plan.id,
            incident_id=incident_id,
            diagnosis_root_cause=plan.diagnosis.root_cause,
            diagnosis_confidence=plan.diagnosis.confidence,
            action_type=plan.action_type,
            risk_level=plan.risk_level,
            requires_approval=plan.requires_approval,
            status=plan.status,
        )
        self.session.add(db_model)
        await self.session.flush()
        return plan


class AuditRepository:
    """Persists AuditLog domain entities to the database."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_event(self, audit_entity: AuditLog) -> AuditLog:
        """
        Persist an AuditLog entity.

        Translates the Pydantic entity to an ORM model internally,
        then returns the original entity.
        """
        db_model = AuditLogModel(
            id=audit_entity.id,
            timestamp=audit_entity.timestamp,
            component=audit_entity.component,
            event=audit_entity.event,
            details=audit_entity.details,
        )
        self.session.add(db_model)
        await self.session.flush()
        return audit_entity
