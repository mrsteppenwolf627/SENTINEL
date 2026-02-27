# 🧠 SENTINEL PROJECT CONTEXT

> **⚠️ CRITICAL RULE FOR AI AGENTS:**
> **EVERY TIME YOU PUSH TO GITHUB, YOU MUST UPDATE THIS FILE WITH THE LATEST CHANGES, DECISIONS, AND NEXT STEPS.**
> This file serves as your persistent memory between sessions. Read it FIRST when starting a new session.

---

## 📅 Last Updated
**Date:** 2026-02-27
**Version:** 2.0-dev (Phase 2 — Persistence Layer complete)
**Status:** Phase 2 in progress / Persistence layer live / LLM Brain next
**Repository:** [https://github.com/mrsteppenwolf627/Sentinel_MPV_V1.git](https://github.com/mrsteppenwolf627/Sentinel_MPV_V1.git)

---

## 📌 Project Overview
**Sentinel** is an autonomous infrastructure agent designed to detect, diagnose, and remediate incidents without human intervention (unless risk is high).

### Current Capabilities (v2.0-dev)
1. **Simulated Ingestion**: Generates fake CPU, Memory, Disk, Latency, and DB-failure alerts (`app/modules/ingestion`).
2. **Rule-Based Analysis**: Maps alerts to diagnoses using static logic with safe metadata handling (`app/modules/analysis`).
3. **Risk Policy**: Classifies actions as SAFE (auto), MODERATE (configurable), or CRITICAL (always requires approval).
4. **Mocked Execution**: Logs actions instead of executing them (safety first).
5. **Audit Trail (dual)**: JSONL file (`AuditService`) + PostgreSQL (`PostgresAuditService`) — both implement `IAuditModule`.
6. **Persistence Layer**: SQLAlchemy 2.0 + Alembic migrations ready. Schema: `incidents`, `remediation_plans`, `audit_logs`.

---

## Environment Setup
- Python venv: `.venv`
- Run: `uvicorn app.main:app --reload`
- DB: `docker-compose up -d && alembic upgrade head`
- Tests: `pytest` → baseline 3/3 passing, 0 warnings

---

## 🏗️ Technical Architecture State

### Module Map
| Module | Implementation File | Responsibility |
| :--- | :--- | :--- |
| **Core** | `app/core/` | Entities (`Alert`, `Incident`, `Diagnosis`, `RemediationPlan`, `AuditLog`), Interfaces, Config, Logger. |
| **Ingestion** | `app/modules/ingestion/simulator.py` | Generates random `Alert` objects. |
| **Analysis** | `app/modules/analysis/engine.py` | Consumes `Alert`, produces `Diagnosis`. |
| **Policy** | `app/modules/policy/risk_manager.py` | Consumes `Diagnosis`, produces `RemediationPlan`. |
| **Action** | `app/modules/action/executors.py` | Executes `RemediationPlan` (Mocked). |
| **Audit (JSONL)** | `app/modules/audit/service.py` | Persists logs to `audit.log` (JSONL). Kept intact. |
| **Audit (DB)** | `app/modules/audit/db_service.py` | `PostgresAuditService` — IAuditModule adapter for PostgreSQL. |
| **DB Models** | `app/infrastructure/database/models.py` | SQLAlchemy ORM: `IncidentModel`, `RemediationPlanModel`, `AuditLogModel`. |
| **Repositories** | `app/infrastructure/database/repositories.py` | Domain-pure repos: accept/return Pydantic entities, map to ORM internally. |
| **Main** | `app/main.py` | FastAPI app, background processing loop, audit UI. |

### Key Design Patterns
- **Hexagonal Architecture**: Infrastructure layer (`app/infrastructure/`) is isolated. Core never imports SQLAlchemy.
- **Domain-Pure Repositories**: Repos accept/return Pydantic entities. ORM ↔ entity mapping is internal to each repo.
- **Dependency Injection**: Modules implement interfaces defined in `app.core.interfaces`.
- **Structured Logging**: All logs use `extra={...}` for JSON parsing via `pythonjsonlogger`.
- **AsyncIO**: The main processing loop is non-blocking.
- **Safe Metadata Formatting**: `rules.py` uses `defaultdict` + `format_map` to prevent `KeyError` on missing metadata keys.

### Key Settings (`app/core/config.py`)
| Setting | Default | Meaning |
| :--- | :--- | :--- |
| `AUTO_APPROVE_MODERATE_ACTIONS` | `True` | If True, MODERATE-risk actions (RESTART, SCALE_UP) execute without human approval. SAFE actions are always auto-approved. CRITICAL always requires approval. |
| `AUDIT_FILE_PATH` | `audit.log` | Path to the JSONL audit log file. |
| `LOG_LEVEL` | `INFO` | Root logging level. |

---

## 📝 Session History (The "Memory")

### Session 1: Genesis & MVP (Feb 5, 2026)
1. **Initialization**: Created strict folder structure (`app/core`, `app/modules`), initialized Git, and set up Python 3.11+ environment.
2. **Implementation**: Built all core modules from scratch following the architecture plan.
3. **Verification**:
   - Encountered missing `aiofiles` and `pytest-asyncio` → **SOLVED** (Installed).
   - Encountered `KeyError` in logger because `message` is a reserved key → **SOLVED** (Renamed to `alert_message` in `engine.py`).
   - Verified end-to-end flow with `pytest` and manual simulation.
4. **Documentation**: Created `SENTINEL_DOCUMENTATION.md` and a user-friendly `README.md`.
5. **Deployment**: Pushed MVP v1.0 to GitHub `main` branch.

### Session 2: Foundation Hardening (Feb 27, 2026)
1. **Full Audit**: Performed a comprehensive read of all source files. Produced `CLAUDE_STATUS.md`.
2. **Bug Fixes Applied** (7 total, 3/3 tests passing, zero deprecation warnings):
   - `main.py`: Added missing `import json`; rewrote `/audit` viewer to parse JSONL and render color-coded HTML.
   - `rules.py`: Replaced `.format(**alert.metadata)` with `.format_map(defaultdict(...))` — eliminates `KeyError` on unknown alert metadata.
   - `entities.py`: Fixed deprecated `datetime.utcnow()` → `datetime.now(timezone.utc)`.
   - `entities.py`: Typed `RemediationPlan.status` as `Literal["PENDING","APPROVED","EXECUTED","FAILED"]`.
   - `config.py`: Replaced deprecated Pydantic V1 `class Config` with `model_config = ConfigDict(...)`.
   - `config.py` + `risk_manager.py`: Renamed misleading `AUTO_APPROVE_SAFE_ACTIONS` → `AUTO_APPROVE_MODERATE_ACTIONS`.
   - `logging.py`: Fixed deprecated `pythonjsonlogger.jsonlogger` → `pythonjsonlogger.json`.
   - `executors.py`: Fixed typo `"Slac/Email"` → `"Slack/Email"`.
3. **Documentation**: Updated all docs to reflect v1.1 state.

### Session 3: Phase 2 — Persistence Layer (Feb 27, 2026)
1. **Design Review**: Read `PHASE_2_PERSISTENCE_DESIGN.md` and identified 3 mandatory corrections before implementation.
2. **Corrections applied to design before coding**:
   - All `datetime.utcnow` in SQLAlchemy models replaced with `lambda: datetime.now(timezone.utc)`.
   - Repositories made domain-pure (accept/return Pydantic entities, not ORM models).
   - `Incident` entity added to `app/core/entities.py` (missing from Phase 1).
3. **New files created**:
   - `app/core/entities.py` → added `Incident` entity (lifecycle: OPEN → ANALYZING → MITIGATING → CLOSED).
   - `app/infrastructure/__init__.py` — infrastructure package.
   - `app/infrastructure/database/__init__.py` — database sub-package.
   - `app/infrastructure/database/models.py` — `IncidentModel`, `RemediationPlanModel`, `AuditLogModel`.
   - `app/infrastructure/database/repositories.py` — `IncidentRepository`, `PlanRepository`, `AuditRepository` (all domain-pure).
   - `app/modules/audit/db_service.py` — `PostgresAuditService` (IAuditModule adapter for PostgreSQL).
   - `docker-compose.yml` — PostgreSQL 15-alpine with healthcheck and named volume.
   - `alembic/` — full async Alembic setup with configured `alembic.ini` and `alembic/env.py`.
   - `alembic/versions/a39f60d0d637_initial_schema.py` — complete initial migration with upgrade/downgrade.
4. **requirements.txt updated**: Added `sqlalchemy>=2.0.0`, `alembic>=1.13.0`, `asyncpg>=0.29.0`, `aiosqlite>=0.20.0`, `psycopg2-binary>=2.9.9`.
5. **Verification**: 3/3 tests passing, 0 warnings after all changes. JSONL `AuditService` untouched and coexists with new `PostgresAuditService`.
6. **Note on `alembic upgrade head`**: Requires Docker Desktop running first (`docker-compose up -d`).

---

## 🛣️ Active Roadmap (Next Steps)

**Phase 2 — Progress:**
1. [x] **Persistence Layer**: SQLAlchemy 2.0 + Alembic + Docker Compose. Run `docker-compose up -d && alembic upgrade head` to activate.
2. [ ] **LLM Brain**: Replace/augment `RuleBasedAnalyzer` with LangChain + Claude API for semantic Root Cause Analysis.
3. [ ] **LangGraph Orchestration**: Refactor the `process_alert` loop into a proper LangGraph agent graph.
4. [ ] **Real Ingestion**: Add a webhook endpoint to receive alerts from Prometheus/Grafana/Datadog.
5. [ ] **Human Approval Workflow**: API endpoints + minimal UI for approving/rejecting CRITICAL plans.

**Phase 3 — Long-term Vision:**
- Redis for real-time event streaming.
- Slack/PagerDuty integration.
- Real action executors (SSH, K8s API, AWS SDK).
- React Dashboard.
- SaaS Multi-tenancy.

---

## 🛑 Operational Rules
1. **Context First**: Always check this file to know where we left off.
2. **Update on Push**: Never push code without updating "Session History" in this file.
3. **Modular**: Do not break the Interface segregation (ABCs in `app/core/interfaces.py`).
4. **Tests**: If you write code, you write tests. Current baseline: 3/3 passing.
5. **Zero Warnings**: Maintain zero deprecation warnings in `pytest` output before pushing.
