# 🛡️ Sentinel — Documentación Técnica

**Versión:** 2.0-dev (Phase 2 — Persistence Layer)
**Fecha:** 27 de Febrero, 2026

---

## 📖 Introducción y Visión

**Sentinel** es un sistema de agente autónomo diseñado para la gestión y auto-remediación de incidentes de infraestructura. Su objetivo es recibir alertas, diagnosticar causas raíz, evaluar riesgos y ejecutar acciones correctivas automáticamente o solicitar aprobación humana cuando sea necesario.

**Visión a Futuro:**
Este proyecto es la semilla de un **SaaS de Observabilidad y Remediación Autónoma** a escala global. El objetivo final es integrar LLMs avanzados para diagnósticos complejos y conectores reales con nubes (AWS, Azure, GCP), Kubernetes y sistemas legacy.

---

## 🏗️ Arquitectura y Estructura del Proyecto

El sistema sigue una **Arquitectura Hexagonal** para garantizar que cada componente sea reemplazable sin afectar al resto. La regla central: el núcleo (`app/core`) nunca importa la infraestructura (`app/infrastructure`).

### Árbol de Directorios
```text
Sentinel/
├── app/
│   ├── main.py                    # 🚀 Punto de entrada (API FastAPI y Loop de control)
│   ├── core/                      # 🧠 Cerebro y Contratos — capa más interna, sin dependencias externas
│   │   ├── entities.py            # Modelos de dominio: Alert, Incident, Diagnosis, RemediationPlan, AuditLog
│   │   ├── interfaces.py          # Interfaces base (ABCs): IIngestionModule, IAnalysisModule, etc.
│   │   ├── config.py              # Configuración global (Pydantic V2 Settings)
│   │   └── logging.py             # Logger estructurado JSON via python-json-logger
│   ├── modules/                   # 🧩 Adaptadores de aplicación
│   │   ├── ingestion/             # AlertSimulator — genera alertas simuladas
│   │   ├── analysis/              # RuleBasedAnalyzer — motor de reglas determinista
│   │   ├── policy/                # RiskEvaluator — matriz Safe/Moderate/Critical
│   │   ├── action/                # ActionExecutor — ejecución mockeada
│   │   └── audit/
│   │       ├── service.py         # AuditService — persistencia JSONL en audit.log (INTACTO)
│   │       └── db_service.py      # PostgresAuditService — IAuditModule para PostgreSQL (NUEVO)
│   ├── infrastructure/            # 🗄️ Capa de infraestructura — solo conoce SQLAlchemy
│   │   └── database/
│   │       ├── models.py          # ORM: IncidentModel, RemediationPlanModel, AuditLogModel
│   │       └── repositories.py   # Domain-pure repos: mapean entidad ↔ ORM internamente
│   └── tests/                     # 🧪 Tests automatizados
├── alembic/                       # Migraciones de base de datos (async)
│   ├── env.py                     # Configurado con Base.metadata de models.py
│   └── versions/
│       └── a39f60d0d637_*.py      # Migración inicial: incidents, remediation_plans, audit_logs
├── alembic.ini                    # URL: postgresql+asyncpg://postgres:postgrespassword@localhost:5432/sentinel
├── docker-compose.yml             # PostgreSQL 15-alpine con healthcheck
├── requirements.txt               # 14 dependencias Python
├── PROJECT_CONTEXT.md             # Memoria central del proyecto
├── SENTINEL_DOCUMENTATION.md     # 📄 Este documento
└── README.md                      # Guía de inicio rápido
```

### Flujo de Datos (Pipeline — sin cambios en v2.0)
El bucle principal (`processing_loop` en `main.py`) no cambió. Solo cambia el adaptador de auditoría inyectado:

```
AlertSimulator
      │  Alert
      ▼
RuleBasedAnalyzer
      │  Diagnosis
      ▼
RiskEvaluator
      │  RemediationPlan
      ▼
ActionExecutor ──── (si requires_approval=False)
      │  bool (success)
      ▼
IAuditModule ─────── AuditService (JSONL)  ← actual
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

### `Incident` *(nuevo en v2.0)*
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

### `Diagnosis`
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `alert_id` | `str` | ID de la alerta analizada |
| `root_cause` | `str` | Causa raíz identificada |
| `confidence` | `float` | 0.0–1.0 (1.0 para reglas deterministas) |
| `suggested_actions` | `list[ActionType]` | Acciones sugeridas ordenadas por preferencia |

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

## 🗄️ Capa de Persistencia (`app/infrastructure/database/`) *(nueva en v2.0)*

### Principio de diseño
El núcleo de la aplicación (`app/core`, `app/modules`) **nunca importa SQLAlchemy**. Los repositorios son los únicos que conocen los modelos ORM. Hacia afuera solo hablan en entidades Pydantic.

### Modelos ORM (`models.py`)
| Tabla | Modelo ORM | Entidad de Dominio |
| :--- | :--- | :--- |
| `incidents` | `IncidentModel` | `Incident` |
| `remediation_plans` | `RemediationPlanModel` | `RemediationPlan` |
| `audit_logs` | `AuditLogModel` | `AuditLog` |

### Repositorios (`repositories.py`)
| Clase | Método principal | Entrada / Salida |
| :--- | :--- | :--- |
| `IncidentRepository` | `save(incident: Incident)` | Pydantic `Incident` → Pydantic `Incident` |
| `IncidentRepository` | `get_by_id(id: str)` | `str` → `Optional[Incident]` |
| `PlanRepository` | `save(plan, incident_id)` | Pydantic `RemediationPlan` → Pydantic `RemediationPlan` |
| `AuditRepository` | `log_event(audit: AuditLog)` | Pydantic `AuditLog` → Pydantic `AuditLog` |

### Servicios de Auditoría (coexisten)
| Clase | Archivo | Backend | Cuándo usar |
| :--- | :--- | :--- | :--- |
| `AuditService` | `modules/audit/service.py` | Archivo JSONL | Desarrollo local rápido, sin Docker |
| `PostgresAuditService` | `modules/audit/db_service.py` | PostgreSQL | Staging y producción, con Docker activo |

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

> **Nota:** El flag `AUTO_APPROVE_MODERATE_ACTIONS` (por defecto `True`) controla exclusivamente las acciones MODERATE. SAFE siempre se auto-aprueba; CRITICAL nunca.

---

## 🛠️ Cómo Funciona y Se Ejecuta

### Requisitos Previos
- Python 3.11+
- Docker Desktop (para PostgreSQL — opcional en desarrollo)

### Instalación
```bash
# Activar entorno virtual
./.venv/Scripts/Activate.ps1        # Windows
source .venv/bin/activate           # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Levantar la base de datos (opcional)
```bash
# Levantar PostgreSQL
docker-compose up -d

# Aplicar migraciones
alembic upgrade head
```

### Ejecución del Agente
```bash
uvicorn app.main:app --reload
```
Una vez iniciado, el sistema procesará alertas simuladas automáticamente cada 5 segundos.

### Endpoints Disponibles
| Endpoint | Método | Descripción |
| :--- | :--- | :--- |
| `/` | GET | Health check, lista de módulos activos |
| `/docs` | GET | Swagger UI automático de FastAPI |
| `/audit` | GET | Visor HTML de los últimos 50 eventos de auditoría |
| `/simulate` | POST | Inyección manual de una alerta personalizada |

### Ejemplo de inyección manual
```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test-server",
    "severity": "CRITICAL",
    "message": "Database connection refused",
    "metadata": {"error_code": 5003}
  }'
```

### Ejecutar Tests
```bash
pytest -v
```
**Estado actual:** 3/3 passing, 0 warnings.

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
- [x] Modelos Pydantic V2 con tipos estrictos y datetimes UTC-aware.
- [x] 3/3 tests pasando, cero deprecation warnings.

### 🔄 Fase 2: Brain & Persistence (En Progreso)
- [x] **Capa de Persistencia**: `app/infrastructure/database/` con SQLAlchemy 2.0, Alembic async, Docker Compose.
- [x] **Entidad `Incident`**: ciclo de vida OPEN → ANALYZING → MITIGATING → CLOSED.
- [x] **Repositorios domain-pure**: mapeo entidad ↔ ORM interno, el núcleo no conoce SQLAlchemy.
- [x] **`PostgresAuditService`**: IAuditModule adapter para PostgreSQL, coexiste con JSONL.
- [ ] **LLM Brain**: Integrar Claude API (langchain-anthropic) en un nuevo `LLMAnalyzer`.
- [ ] **LangGraph**: Refactorizar el loop de procesamiento en un agente LangGraph.
- [ ] **Webhook Ingestion**: Endpoint real para Prometheus/Grafana Alertmanager.
- [ ] **Human Approval API**: Endpoints POST /plans/{id}/approve y /plans/{id}/reject.

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
Añade una entrada en la lista `COMMON_RULES` en `app/modules/analysis/rules.py`:
```python
Rule(
    name="High Latency",
    condition=lambda a: "latency" in a.message.lower(),
    root_cause_template="Service latency exceeded threshold: {latency_ms}ms",
    suggested_actions=[ActionType.SCALE_UP, ActionType.NOTIFICATION]
)
```
Las claves de metadata que no existan se renderizarán como `"N/A"` de forma segura.

### Activar PostgreSQL como backend de auditoría
En `app/main.py`, reemplaza la instancia de `AuditService` por `PostgresAuditService`:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.db_service import PostgresAuditService

# En el lifespan o en un FastAPI Dependency:
audit_service = PostgresAuditService(session=db_session)
```
El `PostgresAuditService` implementa `IAuditModule`, por lo que el resto del código no necesita cambios.

### Logging
Siempre usa `logger.info(msg, extra={...})` pasando diccionarios en `extra` para mantener estructura JSON. **No uses `message` como clave en `extra`** (es una clave reservada del sistema de logging de Python — usa `alert_message` u otra alternativa).

---

*Documentación mantenida por Claude Code — Lead Implementation Engineer.*
