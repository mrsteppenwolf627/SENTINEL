# 📊 Resumen Ejecutivo del Proyecto: Sentinel

**Fecha de actualización:** 27 de Febrero de 2026
**Versión Actual:** 2.0-dev — Phase 2b (LLM Brain)

---

## 🎯 ¿Qué es Sentinel?
Sentinel es un sistema de agente autónomo diseñado para la gestión y auto-remediación de incidentes de infraestructura. Actúa como un "ingeniero de guardia" virtual que detecta, enriquece con historial, diagnostica con IA y resuelve problemas en servidores de forma autónoma, pidiendo ayuda humana solo cuando el riesgo de la acción lo requiere.

---

## ✅ Fase 1 — MVP 1.1 (Foundation Hardened) — Completado

El Producto Mínimo Viable está completamente implementado y endurecido.

### Módulos Implementados
- **Ingestion:** `AlertSimulator` — genera 5 escenarios de alertas reales (CPU, Memoria, Disco, Latencia, DB).
- **Analysis:** `RuleBasedAnalyzer` — 4 reglas deterministas con formateo seguro de metadata (sin riesgo de KeyError). Ahora actúa como **fallback** del LLM.
- **Policy:** `RiskEvaluator` — matriz Safe/Moderate/Critical.
- **Action:** `ActionExecutor` — ejecutor mockeado que simula y registra acciones sin tocar infraestructura real.
- **Audit (JSONL):** `AuditService` — persistencia asíncrona en `audit.log` formato JSONL.
- **Orquestación:** Loop asíncrono no bloqueante gestionado por el `lifespan` de FastAPI.

### Calidad del Código
| Métrica | Estado |
| :--- | :--- |
| Tests | ✅ 5/5 passing |
| Warnings en pytest | ✅ 0 |
| Imports rotos | ✅ 0 |
| Tipos sin validar | ✅ 0 |

---

## ✅ Fase 2a — Persistence Layer — Completado

### Implementado
- **Entidad `Incident`** — ciclo de vida `OPEN → ANALYZING → MITIGATING → CLOSED`.
- **`app/infrastructure/database/models.py`** — Modelos SQLAlchemy: `IncidentModel`, `RemediationPlanModel`, `AuditLogModel`.
- **`app/infrastructure/database/repositories.py`** — Repositorios domain-pure (Pydantic ↔ ORM internamente).
- **`app/modules/audit/db_service.py`** — `PostgresAuditService` implementa `IAuditModule` para PostgreSQL.
- **`docker-compose.yml`** — PostgreSQL 15-alpine con healthcheck y volumen persistente.
- **`alembic/`** — Setup async completo. Migración inicial lista.

---

## ✅ Fase 2b — LLM Brain — Completado

### LLM como cerebro principal

El `LLMAnalyzer` reemplaza a `RuleBasedAnalyzer` como analizador primario cuando `ANTHROPIC_API_KEY` está configurado. Produce diagnósticos causales con cadena de razonamiento y confianza validada.

#### Componentes nuevos
- **`LLMAnalyzer`** (`app/modules/analysis/llm_analyzer.py`):
  - Usa `langchain-anthropic` con `with_structured_output(_LLMDiagnosisOutput)`.
  - Sin librería `instructor`. Extracción confiable via tool_use nativo de Anthropic.
  - Fallback automático y transparente al `RuleBasedAnalyzer` en cualquier error.
  - Configurable: `ANTHROPIC_API_KEY` y `LLM_MODEL` en `.env`.

- **`ContextBuilderService`** (`app/modules/context/builder.py`):
  - Enriquece cada alerta con historial de PostgreSQL antes del análisis.
  - Consulta incidentes similares recientes (24h, mismo `source` o `severity`).
  - Consulta remediaciones ejecutadas pasadas para el mismo `source` (límite 5).
  - Degradación elegante: si el DB no está disponible, retorna contexto mínimo.

#### Entidades evolucionadas
- **`EnrichedContext`** — nueva entidad: `alert` + historial de incidentes + historial de remediaciones.
- **`Diagnosis`** — nuevos campos: `alternative_hypotheses`, `reasoning_trace`, validación `Field(ge=0.0, le=1.0)`.
- **`IAnalysisModule`** — contrato actualizado: `analyze(context: EnrichedContext) → Diagnosis`.

#### Repositorios extendidos
- `IncidentRepository.get_recent_similar(source, severity, hours=24)`.
- `PlanRepository.get_past_executed_for_source(source, limit=5)`.

### Pendiente en Fase 2 (2c)
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
| Tests | Pytest + pytest-asyncio | ✅ En uso (5/5, 0 warnings) |
| ORM / Migraciones | SQLAlchemy 2.0 + Alembic | ✅ En uso (Fase 2a) |
| Base de datos | PostgreSQL 15 (Docker) | ✅ Configurado (Fase 2a) |
| Async DB driver | asyncpg + aiosqlite | ✅ Instalado (Fase 2a) |
| LLM Integration | LangChain + Anthropic Claude | ✅ En uso (Fase 2b) |
| LLM Orchestration | LangGraph | ⏳ Fase 2c |
| Event Streaming | Redis | ⏳ Fase 3 |
| Monitoring Ingestion | Prometheus Client | ⏳ Fase 2c |

---

## 📁 Documentación

- `README.md`: Guía rápida de usuario.
- `PROJECT_CONTEXT.md`: Memoria central para agentes e ingenieros (historial de sesiones + roadmap).
- `SENTINEL_DOCUMENTATION.md`: Documentación técnica profunda.
- `CLAUDE_STATUS.md`: Auditoría inicial completa del codebase (Fase 1).
- `PHASE_2_PERSISTENCE_DESIGN.md`: Diseño original de la capa de persistencia.
- `PHASE_2B_LLM_BRAIN_DESIGN.md`: Diseño original del LLM Brain.
