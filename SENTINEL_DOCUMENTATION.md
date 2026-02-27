# 🛡️ Sentinel — Documentación Técnica

**Versión:** 2.0-dev (Phase 2b — LLM Brain)
**Fecha:** 27 de Febrero, 2026

---

## 📖 Introducción y Visión

**Sentinel** es un sistema de agente autónomo diseñado para la gestión y auto-remediación de incidentes de infraestructura. Su objetivo es recibir alertas, enriquecer el contexto con historial de la base de datos, diagnosticar causas raíz usando un LLM, evaluar riesgos y ejecutar acciones correctivas automáticamente o solicitar aprobación humana cuando sea necesario.

**Visión a Futuro:**
Este proyecto es la semilla de un **SaaS de Observabilidad y Remediación Autónoma** a escala global. El objetivo final es integrar LLMs avanzados para diagnósticos complejos y conectores reales con nubes (AWS, Azure, GCP), Kubernetes y sistemas legacy.

---

## 🏗️ Arquitectura y Estructura del Proyecto

El sistema sigue una **Arquitectura Hexagonal** para garantizar que cada componente sea reemplazable sin afectar al resto. La regla central: el núcleo (`app/core`) nunca importa la infraestructura (`app/infrastructure`).

### Árbol de Directorios
```text
Sentinel/
├── app/
│   ├── main.py                      # 🚀 Punto de entrada (API FastAPI y Loop de control)
│   ├── core/                        # 🧠 Cerebro y Contratos — sin dependencias externas
│   │   ├── entities.py              # Alert, Incident, Diagnosis, RemediationPlan,
│   │   │                            #   EnrichedContext, AuditLog
│   │   ├── interfaces.py            # ABCs: IIngestionModule, IAnalysisModule(EnrichedContext), etc.
│   │   ├── config.py                # Pydantic V2 Settings (incl. ANTHROPIC_API_KEY, LLM_MODEL)
│   │   └── logging.py               # Logger estructurado JSON
│   ├── modules/                     # 🧩 Adaptadores de aplicación
│   │   ├── ingestion/               # AlertSimulator — genera alertas simuladas
│   │   ├── analysis/
│   │   │   ├── engine.py            # RuleBasedAnalyzer — motor de reglas (fallback)
│   │   │   ├── rules.py             # COMMON_RULES — 4 reglas deterministas
│   │   │   └── llm_analyzer.py      # LLMAnalyzer — Claude via LangChain (primario)
│   │   ├── context/
│   │   │   └── builder.py           # ContextBuilderService — enriquece Alert con historial DB
│   │   ├── policy/                  # RiskEvaluator — matriz Safe/Moderate/Critical
│   │   ├── action/                  # ActionExecutor — ejecución mockeada
│   │   └── audit/
│   │       ├── service.py           # AuditService — persistencia JSONL en audit.log
│   │       └── db_service.py        # PostgresAuditService — IAuditModule para PostgreSQL
│   ├── infrastructure/              # 🗄️ Capa de infraestructura — solo conoce SQLAlchemy
│   │   └── database/
│   │       ├── models.py            # ORM: IncidentModel, RemediationPlanModel, AuditLogModel
│   │       └── repositories.py      # Domain-pure repos + get_recent_similar,
│   │                                #   get_past_executed_for_source
│   └── tests/
│       └── unit/
│           ├── test_analysis.py     # Tests RuleBasedAnalyzer (usa EnrichedContext)
│           ├── test_audit.py        # Tests AuditService JSONL
│           └── test_llm_analyzer.py # Tests fallback de LLMAnalyzer (sin API real)
├── alembic/                         # Migraciones de base de datos (async)
│   ├── env.py                       # Configurado con Base.metadata de models.py
│   └── versions/
│       └── a39f60d0d637_*.py        # Migración inicial: incidents, remediation_plans, audit_logs
├── alembic.ini                      # URL: postgresql+asyncpg://postgres:postgrespassword@localhost:5432/sentinel
├── docker-compose.yml               # PostgreSQL 15-alpine con healthcheck
├── pytest.ini                       # asyncio_mode=strict, filtro UserWarning Python 3.14
├── .env                             # ANTHROPIC_API_KEY, LLM_MODEL (no versionado)
├── requirements.txt                 # 17 dependencias Python
├── PROJECT_CONTEXT.md               # Memoria central del proyecto
├── SENTINEL_DOCUMENTATION.md       # 📄 Este documento
└── README.md                        # Guía de inicio rápido
```

### Flujo de Datos (Pipeline v2.0-dev — Phase 2b)

```
AlertSimulator
      │  Alert
      ▼
ContextBuilderService  ──► PostgreSQL (incidentes recientes + remediaciones pasadas)
      │  EnrichedContext
      ▼
LLMAnalyzer (Claude)
      │  si error / sin API key
      └──► RuleBasedAnalyzer (fallback automático)
      │  Diagnosis
      ▼
RiskEvaluator
      │  RemediationPlan
      ▼
ActionExecutor ──── (si requires_approval=False)
      │  bool (success)
      ▼
IAuditModule ─────── AuditService (JSONL)  ← activo por defecto
                └──  PostgresAuditService  ← disponible, activar via DI
```

---

## 🔑 Modelos de Dominio (`app/core/entities.py`)

### `Alert`
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Identificador único generado automáticamente |
| `source` | `str` | Sistema de origen (ej. `"web-server-01"`) |
| `timestamp` | `datetime` | UTC-aware, generado con `datetime.now(timezone.utc)` |
| `severity` | `AlertSeverity` | `INFO \| WARNING \| CRITICAL \| FATAL` |
| `message` | `str` | Descripción del incidente |
| `metadata` | `dict` | Datos adicionales (ej. `{"cpu_usage": 95}`) |

### `Incident`
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Identificador único generado automáticamente |
| `alert_id` | `str` | ID de la alerta que originó el incidente |
| `source` | `str` | Sistema de origen |
| `severity` | `AlertSeverity` | Severidad heredada de la alerta |
| `message` | `str` | Descripción del incidente |
| `metadata` | `dict` | Datos adicionales |
| `status` | `Literal` | `"OPEN" \| "ANALYZING" \| "MITIGATING" \| "CLOSED"` |
| `created_at` | `datetime` | UTC-aware, auto-generado |
| `closed_at` | `Optional[datetime]` | Momento de cierre, `None` mientras activo |

### `Diagnosis` *(actualizado en v2.0-dev Phase 2b)*
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `alert_id` | `str` | ID de la alerta analizada |
| `root_cause` | `str` | Causa raíz identificada |
| `confidence` | `float` | 0.0–1.0 (validado con `Field(ge=0.0, le=1.0)`) |
| `alternative_hypotheses` | `list[str]` | Hipótesis alternativas evaluadas (LLM) |
| `reasoning_trace` | `str` | Cadena de razonamiento paso a paso (LLM); `""` para el rule engine |
| `suggested_actions` | `list[ActionType]` | Acciones sugeridas ordenadas por preferencia |

### `EnrichedContext` *(nuevo en v2.0-dev Phase 2b)*
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `alert` | `Alert` | La alerta original que disparó el análisis |
| `recent_similar_incidents` | `list[Incident]` | Incidentes recientes (24h) con mismo `source` o `severity` |
| `past_remediations_for_source` | `list[RemediationPlan]` | Últimas 5 remediaciones ejecutadas para ese `source` |

### `RemediationPlan`
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | ID del plan |
| `diagnosis` | `Diagnosis` | Diagnóstico que origina el plan |
| `action_type` | `ActionType` | Acción a ejecutar |
| `risk_level` | `RiskLevel` | `SAFE \| MODERATE \| CRITICAL` |
| `requires_approval` | `bool` | Si requiere aprobación humana |
| `status` | `Literal` | `"PENDING" \| "APPROVED" \| "EXECUTED" \| "FAILED"` |

---

## 🧠 LLM Brain (`app/modules/analysis/llm_analyzer.py`) *(nuevo en Phase 2b)*

### Principio de diseño
El `LLMAnalyzer` recibe un `EnrichedContext` (con historial de DB) y llama a Claude para producir un `Diagnosis` con cadena de razonamiento causal. No usa la librería `instructor` — utiliza `ChatAnthropic.with_structured_output(_LLMDiagnosisOutput)` de LangChain para extracción Pydantic confiable via tool_use nativo de Anthropic.

### Esquema interno `_LLMDiagnosisOutput`
Modelo Pydantic interno que el LLM rellena (excluye `alert_id` para evitar que el LLM lo invente):
```python
class _LLMDiagnosisOutput(BaseModel):
    root_cause: str
    confidence: float          # Field(ge=0.0, le=1.0)
    alternative_hypotheses: List[str]
    reasoning_trace: str
    suggested_actions: List[ActionType]
```
Tras la llamada, se construye el `Diagnosis` final inyectando `alert_id=context.alert.id`.

### Fallback automático
```
LLMAnalyzer.analyze(context)
    → intenta _call_llm(context)
    → si cualquier excepción → logger.warning + fallback.analyze(context)
```
La degradación es transparente. El resto del pipeline no sabe si el resultado vino del LLM o del rule engine.

### Activación
Crear `.env` en la raíz del proyecto:
```env
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-4-6     # opcional, este es el default
```
Si `ANTHROPIC_API_KEY` está vacío, `main.py` usa directamente `RuleBasedAnalyzer`.

---

## 🌍 ContextBuilderService (`app/modules/context/builder.py`) *(nuevo en Phase 2b)*

Antes de llamar al analizador, el orquestador pasa por `ContextBuilderService.build(alert)` que:

1. Consulta `IncidentRepository.get_recent_similar(source, severity, hours=24)` — incidentes en las últimas 24h que compartan `source` o `severity`.
2. Consulta `PlanRepository.get_past_executed_for_source(source, limit=5)` — las últimas 5 remediaciones ejecutadas para ese `source`.
3. Retorna `EnrichedContext(alert=alert, recent_similar_incidents=..., past_remediations_for_source=...)`.

**Degradación elegante**: si PostgreSQL no está disponible, captura la excepción y retorna `EnrichedContext(alert=alert)` con listas vacías. El LLM recibe menos contexto pero el pipeline no falla.

---

## 🗄️ Capa de Persistencia (`app/infrastructure/database/`)

### Principio de diseño
El núcleo (`app/core`, `app/modules`) **nunca importa SQLAlchemy**. Los repositorios son los únicos que conocen los modelos ORM.

### Modelos ORM (`models.py`)
| Tabla | Modelo ORM | Entidad de Dominio |
| :--- | :--- | :--- |
| `incidents` | `IncidentModel` | `Incident` |
| `remediation_plans` | `RemediationPlanModel` | `RemediationPlan` |
| `audit_logs` | `AuditLogModel` | `AuditLog` |

### Repositorios (`repositories.py`)
| Clase | Método | Descripción |
| :--- | :--- | :--- |
| `IncidentRepository` | `save(incident)` | Persiste un `Incident` |
| `IncidentRepository` | `get_by_id(id)` | Recupera por ID |
| `IncidentRepository` | `get_recent_similar(source, severity, hours=24)` | Incidentes similares recientes |
| `PlanRepository` | `save(plan, incident_id)` | Persiste un `RemediationPlan` |
| `PlanRepository` | `get_past_executed_for_source(source, limit=5)` | Remediaciones pasadas ejecutadas |
| `AuditRepository` | `log_event(audit)` | Persiste un `AuditLog` |

### Servicios de Auditoría (coexisten)
| Clase | Archivo | Backend | Cuándo usar |
| :--- | :--- | :--- | :--- |
| `AuditService` | `modules/audit/service.py` | Archivo JSONL | Desarrollo local rápido, sin Docker |
| `PostgresAuditService` | `modules/audit/db_service.py` | PostgreSQL | Staging y producción, con Docker activo |

---

## ⚙️ Configuración (`app/core/config.py`)

| Setting | Default | Descripción |
| :--- | :--- | :--- |
| `ANTHROPIC_API_KEY` | `""` | API key de Claude. Si está vacío, se usa el rule engine. |
| `LLM_MODEL` | `claude-sonnet-4-6` | Modelo de Claude usado por `LLMAnalyzer`. |
| `DATABASE_URL` | `postgresql+asyncpg://...` | URL async de PostgreSQL para repos y context builder. |
| `AUTO_APPROVE_MODERATE_ACTIONS` | `True` | Si True, acciones MODERATE se auto-ejecutan. |
| `AUDIT_FILE_PATH` | `audit.log` | Ruta del log JSONL. |
| `LOG_LEVEL` | `INFO` | Nivel de logging raíz. |

---

## ⚙️ Política de Riesgo (`app/modules/policy/risk_manager.py`)

| ActionType | RiskLevel | Auto-ejecuta |
| :--- | :--- | :--- |
| `NOTIFICATION` | SAFE | ✅ Siempre |
| `CLEAR_CACHE` | SAFE | ✅ Siempre |
| `SCALE_UP` | MODERATE | ⚙️ Si `AUTO_APPROVE_MODERATE_ACTIONS=True` |
| `RESTART_SERVICE` | MODERATE | ⚙️ Si `AUTO_APPROVE_MODERATE_ACTIONS=True` |
| `BLOCK_IP` | MODERATE | ⚙️ Si `AUTO_APPROVE_MODERATE_ACTIONS=True` |
| `MANUAL_INTERVENTION` | CRITICAL | ❌ Nunca (siempre requiere aprobación) |

---

## 🛠️ Cómo Funciona y Se Ejecuta

### Requisitos Previos
- Python 3.11+
- Docker Desktop (para PostgreSQL — opcional)
- API key de Anthropic (para LLM Brain — opcional)

### Instalación
```bash
# Activar entorno virtual
./.venv/Scripts/Activate.ps1        # Windows
source .venv/bin/activate           # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Configurar LLM Brain (opcional)
```bash
# Crear .env en la raíz del proyecto
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Levantar la base de datos (opcional)
```bash
docker-compose up -d
alembic upgrade head
```

### Ejecución del Agente
```bash
uvicorn app.main:app --reload
```
El endpoint `/` muestra qué analizador está activo (`LLMAnalyzer` o `RuleBasedAnalyzer`).

### Endpoints Disponibles
| Endpoint | Método | Descripción |
| :--- | :--- | :--- |
| `/` | GET | Health check + analizador activo |
| `/docs` | GET | Swagger UI automático de FastAPI |
| `/audit` | GET | Visor HTML de los últimos 50 eventos de auditoría |
| `/simulate` | POST | Inyección manual de una alerta personalizada |

### Ejecutar Tests
```bash
pytest -v
```
**Estado actual:** 5/5 passing, 0 warnings.

---

## 🛣️ Roadmap y Estado del Proyecto

### ✅ Fase 1: MVP 1.1 — Foundation Hardened (Completado)
- [x] Estructura base, Git y logging estructurado JSON.
- [x] Simulador de alertas (CPU, Memoria, Disco, Latencia, DB).
- [x] Motor de reglas determinista con formateo seguro de metadata.
- [x] Política de riesgo Safe/Moderate/Critical con flag correctamente nombrado.
- [x] Ejecutor mockeado (simula reinicios, escalados, notificaciones).
- [x] Auditoría JSONL asíncrona.
- [x] Orquestación asíncrona en background con FastAPI lifespan.
- [x] Visor de auditoría HTML con color-coding por severidad.
- [x] 5/5 tests pasando, cero warnings.

### ✅ Fase 2a: Persistence Layer (Completado)
- [x] `app/infrastructure/database/` con SQLAlchemy 2.0, Alembic async, Docker Compose.
- [x] Entidad `Incident`: ciclo de vida OPEN → ANALYZING → MITIGATING → CLOSED.
- [x] Repositorios domain-pure: mapeo entidad ↔ ORM interno, el núcleo no conoce SQLAlchemy.
- [x] `PostgresAuditService`: IAuditModule adapter para PostgreSQL, coexiste con JSONL.

### ✅ Fase 2b: LLM Brain (Completado)
- [x] **`LLMAnalyzer`**: Claude via `langchain-anthropic`, `with_structured_output`, fallback automático.
- [x] **`ContextBuilderService`**: enriquece Alert con historial de DB antes del análisis.
- [x] **`EnrichedContext`**: nueva entidad de dominio con alert + historial.
- [x] **`Diagnosis` evolucionado**: `alternative_hypotheses`, `reasoning_trace`, validación `ge/le`.
- [x] **`IAnalysisModule`** actualizado: `analyze(context: EnrichedContext)`.
- [x] **Repositorios extendidos**: `get_recent_similar`, `get_past_executed_for_source`.

### 🔄 Fase 2c: Orquestación y Aprobación (Próximo)
- [ ] **LangGraph**: Refactorizar el loop de procesamiento en un agente LangGraph.
- [ ] **Webhook Ingestion**: Endpoint real para Prometheus/Grafana Alertmanager.
- [ ] **Human Approval API**: `POST /plans/{id}/approve` y `/plans/{id}/reject`.

### 🌐 Fase 3: Conectores Reales
- [ ] Integración Slack/PagerDuty.
- [ ] Ejecutores reales (SSH via Paramiko, Kubernetes API, AWS SDK).
- [ ] Redis para streaming de eventos.
- [ ] Dashboard React.
- [ ] Multi-tenancy SaaS.

---

## 💡 Guía para Desarrolladores y Agentes LLM

### Añadir una nueva fuente de alertas
1. Crea una clase en `app/modules/ingestion/` que implemente `IIngestionModule`.
2. Expórtala desde `app/modules/ingestion/__init__.py`.
3. Úsala en `app/main.py` en lugar de (o junto a) `AlertSimulator`.

### Añadir una nueva regla de detección
Añade una entrada en `COMMON_RULES` en `app/modules/analysis/rules.py`:
```python
Rule(
    name="High Latency",
    condition=lambda a: "latency" in a.message.lower(),
    root_cause_template="Service latency exceeded threshold: {latency_ms}ms",
    suggested_actions=[ActionType.SCALE_UP, ActionType.NOTIFICATION]
)
```
Las claves de metadata que no existan se renderizarán como `"N/A"` de forma segura.

### Activar el LLM Brain
Crea `.env` con `ANTHROPIC_API_KEY`. El `main.py` detecta automáticamente la clave y usa `LLMAnalyzer`. Sin clave, usa `RuleBasedAnalyzer`. El endpoint `/` muestra cuál está activo.

### Activar PostgreSQL como backend de auditoría
En `app/main.py`, reemplaza la instancia de `AuditService` por `PostgresAuditService`:
```python
from app.modules.audit.db_service import PostgresAuditService
audit_service = PostgresAuditService(session=db_session)
```
El `PostgresAuditService` implementa `IAuditModule`, el resto del código no cambia.

### Escribir tests para nuevos analizadores
Los tests deben pasar `EnrichedContext` (no `Alert` directamente):
```python
from app.core.entities import Alert, AlertSeverity, EnrichedContext

context = EnrichedContext(alert=Alert(
    source="server-01",
    severity=AlertSeverity.CRITICAL,
    message="High CPU usage",
    metadata={"cpu_usage": 99, "component": "cpu"}
))
diagnosis = await analyzer.analyze(context)
```

### Logging
Siempre usa `logger.info(msg, extra={...})` con diccionarios en `extra`. **No uses `message` como clave en `extra`** (clave reservada de Python logging — usa `alert_message`).

---

*Documentación mantenida por Claude Code — Lead Implementation Engineer.*
