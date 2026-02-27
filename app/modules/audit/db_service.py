"""
PostgresAuditService — Database-backed implementation of IAuditModule.

This is an Adapter in the Hexagonal Architecture sense: it implements the
core port (IAuditModule) and delegates to the infrastructure layer
(AuditRepository / SQLAlchemy). The core processing pipeline never knows
that Postgres is involved — it only calls IAuditModule.log_event().

Coexists with the file-based AuditService (service.py). Both implement
IAuditModule and can be swapped via dependency injection in main.py.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities import AuditLog
from app.core.interfaces import IAuditModule
from app.infrastructure.database.repositories import AuditRepository


class PostgresAuditService(IAuditModule):
    """
    IAuditModule adapter that persists events to PostgreSQL.

    Requires an active AsyncSession injected at construction time.
    The caller is responsible for committing or rolling back the session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repository = AuditRepository(session)

    async def log_event(self, log: AuditLog) -> None:
        """Persist the audit event to the database via AuditRepository."""
        await self._repository.log_event(log)
