"""
Repository implementations for the Sentinel persistence layer.

DESIGN RULE (Correction 2):
All repositories accept and return Pydantic domain entities from app.core.entities.
The translation between Pydantic entity ↔ SQLAlchemy model happens EXCLUSIVELY
inside each repository method. External callers never import or touch SQLAlchemy models.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities import AlertSeverity, AuditLog, Diagnosis, Incident, RemediationPlan
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
        return self._to_entity(db_model)

    async def get_recent_similar(
        self,
        source: str,
        severity: AlertSeverity,
        hours: int = 24,
        limit: int = 10,
    ) -> List[Incident]:
        """Return incidents matching source OR severity within the last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await self.session.execute(
            select(IncidentModel)
            .where(
                and_(
                    or_(IncidentModel.source == source, IncidentModel.severity == severity),
                    IncidentModel.created_at >= cutoff,
                )
            )
            .order_by(IncidentModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, db_model: IncidentModel) -> Incident:
        """Translate an ORM model to a Pydantic Incident entity."""
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

    async def get_past_executed_for_source(
        self, source: str, limit: int = 5
    ) -> List[RemediationPlan]:
        """Return the last N executed plans for incidents from the given source."""
        result = await self.session.execute(
            select(RemediationPlanModel)
            .join(IncidentModel, RemediationPlanModel.incident_id == IncidentModel.id)
            .where(
                and_(
                    IncidentModel.source == source,
                    RemediationPlanModel.status == "EXECUTED",
                )
            )
            .order_by(RemediationPlanModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, db_model: RemediationPlanModel) -> RemediationPlan:
        """Translate an ORM model to a Pydantic RemediationPlan entity.

        NOTE: alert_id and suggested_actions are not stored in the DB at this stage.
        They are reconstructed with safe defaults for context-building purposes.
        """
        diagnosis = Diagnosis(
            alert_id="",
            root_cause=db_model.diagnosis_root_cause,
            confidence=db_model.diagnosis_confidence,
            alternative_hypotheses=[],
            reasoning_trace="",
            suggested_actions=[],
        )
        return RemediationPlan(
            id=db_model.id,
            diagnosis=diagnosis,
            action_type=db_model.action_type,
            risk_level=db_model.risk_level,
            requires_approval=db_model.requires_approval,
            status=db_model.status,
        )


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
