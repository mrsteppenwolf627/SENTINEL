# 🛡️ Sentinel

**Agente Autónomo de Infraestructura — v2.0-dev (Phase 2b)**

> *Un sistema inteligente que vigila tus servidores, diagnostica problemas y los arregla antes de que te despierten a las 3 A.M.*

---

## 🌟 ¿Qué es Sentinel?

Sentinel es un "guardián digital" para sistemas informáticos. Funciona como un ingeniero experto monitoreando tus servidores las 24 horas del día, listo para actuar en milisegundos si algo falla.

Sentinel puede:
1. **Escuchar**: Detecta alertas simuladas como "CPU al 100%" o "Disco lleno".
2. **Recordar**: Consulta el historial de incidentes y remediaciones en PostgreSQL antes de analizar.
3. **Pensar**: Analiza la causa raíz usando **Claude** (LLM) como cerebro principal, con motor de reglas como respaldo automático.
4. **Decidir**: Evalúa si es peligroso actuar automáticamente o si debe pedir permiso humano.
5. **Actuar**: Ejecuta la solución (reiniciar un servicio, borrar caché, escalar instancias).
6. **Auditar**: Guarda un registro completo — en archivo JSONL o en PostgreSQL.

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar la API key de Claude
Crea un archivo `.env` en la raíz del proyecto:
```env
ANTHROPIC_API_KEY=sk-ant-...tu_clave...
LLM_MODEL=claude-sonnet-4-6
```
Sin este archivo, Sentinel funciona igual usando el motor de reglas como fallback.

### 3. (Opcional) Levantar base de datos PostgreSQL
```bash
docker-compose up -d
alembic upgrade head
```
Si no tienes Docker, Sentinel funciona igual usando el log JSONL local (`audit.log`).

### 4. Encender Sentinel
```bash
uvicorn app.main:app --reload
```

### 5. Observar en tiempo real
Abre tu navegador en `http://127.0.0.1:8000/audit`.

Verás el dashboard de auditoría con color-coding por severidad, mostrando cada alerta detectada y la decisión tomada por el agente — incluyendo el `reasoning_trace` del LLM.

### 6. Inyectar una alerta manual
```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "source": "mi-servidor",
    "severity": "CRITICAL",
    "message": "Database connection refused",
    "metadata": {"error_code": 5003}
  }'
```

### 7. Ejecutar tests
```bash
pytest -v
```
Resultado esperado: **5 passed, 0 warnings**.

---

## 🔧 Endpoints de la API

| Endpoint | Método | Descripción |
| :--- | :--- | :--- |
| `/` | GET | Estado del sistema, analizador activo y módulos |
| `/docs` | GET | Swagger UI interactivo |
| `/audit` | GET | Dashboard HTML de los últimos 50 eventos |
| `/simulate` | POST | Inyección manual de una alerta |

---

## 🏗️ Arquitectura

```
AlertSimulator
      │  Alert
      ▼
ContextBuilderService  ──► PostgreSQL (historial de incidentes y remediaciones)
      │  EnrichedContext
      ▼
LLMAnalyzer (Claude)  ──► [si API key no disponible o falla]
      │                              │
      │                    RuleBasedAnalyzer (fallback)
      │  Diagnosis
      ▼
RiskEvaluator
      │  RemediationPlan
      ▼
ActionExecutor
      │  bool (success)
      ▼
IAuditModule
    /        \
AuditService  PostgresAuditService
(audit.log)    (PostgreSQL)
```

Cada componente implementa una interfaz abstracta en `app/core/interfaces.py`, lo que permite reemplazar cualquier pieza sin afectar al resto del sistema.

### Lógica de Riesgo

| Nivel | Acción | Comportamiento |
| :--- | :--- | :--- |
| `SAFE` | NOTIFICATION, CLEAR_CACHE | Auto-ejecuta siempre |
| `MODERATE` | RESTART_SERVICE, SCALE_UP, BLOCK_IP | Auto-ejecuta si `AUTO_APPROVE_MODERATE_ACTIONS=True` |
| `CRITICAL` | MANUAL_INTERVENTION | Siempre requiere aprobación humana |

---

## 🔮 Roadmap

| Fase | Descripción | Estado |
| :--- | :--- | :--- |
| MVP 1.1 | Pipeline completo con motor de reglas, auditoría JSONL y API | ✅ Completo |
| Fase 2a | Capa de persistencia: SQLAlchemy + Alembic + Docker Compose | ✅ Completo |
| Fase 2b | LLM Brain: Claude API + LangChain + ContextBuilderService | ✅ Completo |
| Fase 2c | LangGraph Orchestration + Webhook Ingestion + Human Approval | ⏳ Próximo |
| Fase 3 | Ejecutores reales (SSH, K8s), Slack/PagerDuty, Dashboard React | 🔮 Futuro |

---

## 🗂️ Documentación Adicional

- [`SENTINEL_DOCUMENTATION.md`](./SENTINEL_DOCUMENTATION.md) — Arquitectura técnica profunda, modelos de dominio y guía para desarrolladores.
- [`PROJECT_CONTEXT.md`](./PROJECT_CONTEXT.md) — Memoria del proyecto: historial de sesiones, decisiones de arquitectura y próximos pasos.
- [`RESUMEN_PROYECTO.md`](./RESUMEN_PROYECTO.md) — Resumen ejecutivo del estado actual.
- [`CLAUDE_STATUS.md`](./CLAUDE_STATUS.md) — Auditoría completa del codebase con issues identificados y resueltos.

---

*Hecho con Python, FastAPI, SQLAlchemy y Claude.*
