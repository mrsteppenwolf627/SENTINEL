# 📊 Resumen Ejecutivo del Proyecto: Sentinel

**Fecha de actualización:** 27 de Febrero de 2026
**Versión Actual:** 2.0-dev — Phase 2 (Persistence Layer)

---

## 🎯 ¿Qué es Sentinel?
Sentinel es un sistema de agente autónomo diseñado para la gestión y auto-remediación de incidentes de infraestructura. Actúa como un "ingeniero de guardia" virtual que detecta, diagnostica y resuelve problemas en servidores de forma autónoma, pidiendo ayuda humana solo cuando el riesgo de la acción lo requiere.

---

## ✅ Fase 1 — MVP 1.1 (Foundation Hardened) — Completado

El Producto Mínimo Viable está completamente implementado. Pasó por una sesión de **hardening** que eliminó todos los errores de cimentación antes de avanzar.

### Módulos Implementados
- **Ingestion:** `AlertSimulator` — genera 5 escenarios de alertas reales (CPU, Memoria, Disco, Latencia, DB).
- **Analysis:** `RuleBasedAnalyzer` — 4 reglas deterministas con formateo seguro de metadata (sin riesgo de KeyError).
- **Policy:** `RiskEvaluator` — matriz Safe/Moderate/Critical. Flag `AUTO_APPROVE_MODERATE_ACTIONS` correctamente nombrado.
- **Action:** `ActionExecutor` — ejecutor mockeado que simula y registra acciones sin tocar infraestructura real.
- **Audit (JSONL):** `AuditService` — persistencia asíncrona en `audit.log` formato JSONL.
- **Orquestación:** Loop asíncrono no bloqueante gestionado por el `lifespan` de FastAPI.

### Calidad del Código (MVP 1.1)
| Métrica | Estado |
| :--- | :--- |
| Tests | ✅ 3/3 passing |
| Deprecation warnings | ✅ 0 |
| Imports rotos | ✅ 0 |
| Typos en código | ✅ 0 |
| Tipos sin validar | ✅ 0 (status tipado como Literal) |

---

## 🔄 Fase 2 — Brain & Persistence (En Progreso)

### Completado en esta fase

#### Capa de Persistencia (Session 3)
- **Entidad `Incident`** añadida a `app/core/entities.py` — ciclo de vida `OPEN → ANALYZING → MITIGATING → CLOSED`.
- **`app/infrastructure/database/models.py`** — Modelos SQLAlchemy: `IncidentModel`, `RemediationPlanModel`, `AuditLogModel`. Todos usan `datetime.now(timezone.utc)`.
- **`app/infrastructure/database/repositories.py`** — Repositorios domain-pure: aceptan y devuelven entidades Pydantic; el mapeo ORM es interno.
- **`app/modules/audit/db_service.py`** — `PostgresAuditService` implementa `IAuditModule` para PostgreSQL. Coexiste con `AuditService` (JSONL).
- **`docker-compose.yml`** — PostgreSQL 15-alpine con healthcheck y volumen persistente.
- **`alembic/`** — Setup async completo. Migración inicial lista (`incidents`, `remediation_plans`, `audit_logs`).
- **`requirements.txt`** — Añadidas 5 dependencias: `sqlalchemy`, `alembic`, `asyncpg`, `aiosqlite`, `psycopg2-binary`.

### Pendiente en esta fase
- **LLM Brain:** Integrar Claude API + LangChain en un nuevo `LLMAnalyzer`.
- **LangGraph Orchestration:** Refactorizar el loop en un grafo de agente.
- **Webhook Ingestion:** Endpoint para Prometheus Alertmanager / Grafana / Datadog.
- **Human Approval Workflow:** POST /plans/{id}/approve y /plans/{id}/reject.

---

## 🏛️ Stack Tecnológico

| Capa | Tecnología | Estado |
| :--- | :--- | :--- |
| API Framework | FastAPI + Uvicorn | ✅ En uso |
| Data Models | Pydantic V2 | ✅ En uso |
| Logging | python-json-logger | ✅ En uso |
| Tests | Pytest + pytest-asyncio | ✅ En uso |
| ORM / Migraciones | SQLAlchemy 2.0 + Alembic | ✅ Implementado (Fase 2) |
| Base de datos | PostgreSQL 15 (Docker) | ✅ Configurado (Fase 2) |
| Async DB driver | asyncpg + aiosqlite | ✅ Instalado (Fase 2) |
| LLM Orchestration | LangGraph | ⏳ Fase 2 |
| LLM Integration | LangChain + Anthropic Claude | ⏳ Fase 2 |
| Event Streaming | Redis | ⏳ Fase 3 |
| Monitoring Ingestion | Prometheus Client | ⏳ Fase 2 |

---

## 📁 Documentación

- `README.md`: Guía rápida de usuario con instrucciones Docker.
- `PROJECT_CONTEXT.md`: Memoria central para agentes e ingenieros (historial de sesiones + roadmap).
- `SENTINEL_DOCUMENTATION.md`: Documentación técnica profunda con pipeline, modelos y guía de desarrollo.
- `CLAUDE_STATUS.md`: Auditoría inicial completa del codebase (Fase 1).
- `PHASE_2_PERSISTENCE_DESIGN.md`: Diseño original de la capa de persistencia.
