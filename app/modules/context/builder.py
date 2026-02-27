"""
ContextBuilderService: enriches a raw Alert with historical data from PostgreSQL
before passing it to the analysis module.

Gracefully degrades: if the database is unavailable, returns minimal EnrichedContext
with empty history so the rest of the pipeline is unaffected.
"""
from typing import Callable, Optional

from app.core.entities import Alert, EnrichedContext
from app.core.logging import logger
from app.infrastructure.database.repositories import IncidentRepository, PlanRepository


class ContextBuilderService:
    """
    Queries PostgreSQL to build an EnrichedContext for a given Alert.

    Injected with an async session factory so it can open its own session
    per call. If session_factory is None (e.g. in tests or when DB is off),
    it returns a minimal context containing only the alert.
    """

    def __init__(self, session_factory: Optional[Callable] = None) -> None:
        self._session_factory = session_factory

    async def build(self, alert: Alert) -> EnrichedContext:
        """Build an EnrichedContext for the given alert.

        Returns EnrichedContext with empty history if the DB is unavailable.
        """
        if self._session_factory is None:
            return EnrichedContext(alert=alert)

        try:
            async with self._session_factory() as session:
                incident_repo = IncidentRepository(session)
                plan_repo = PlanRepository(session)

                recent = await incident_repo.get_recent_similar(
                    source=alert.source,
                    severity=alert.severity,
                )
                past = await plan_repo.get_past_executed_for_source(
                    source=alert.source,
                )

                return EnrichedContext(
                    alert=alert,
                    recent_similar_incidents=recent,
                    past_remediations_for_source=past,
                )
        except Exception as exc:
            logger.warning(
                "ContextBuilder could not reach DB — using minimal context",
                extra={"error": str(exc)[:200]},
            )
            return EnrichedContext(alert=alert)
