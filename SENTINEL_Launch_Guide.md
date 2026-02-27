# 🛡️ SENTINEL — Guía de Arranque con Dual-LLM Strategy
## Claude Code (Antigravity) + Gemini 2.5 Pro (Agent Bar)

---

## 🧠 PREPARACIÓN MENTAL: Lo que estás a punto de construir

### La magnitud real del proyecto

Sentinel no es otro proyecto de portfolio. Según el análisis estratégico que has desarrollado:

- El mercado AIOps va a **303,000 millones USD para 2035** (CAGR 22.95%)
- El coste de **1 minuto de caída** en banca/telco supera los **$5,000**
- Un agente que detecta y mitiga en segundos vs. 45-60 min humanos = **ROI casi inmediato**
- El 67% de los SREs no tienen tiempo para formación por el "toil" manual

Tú vas a construir exactamente lo que ese mercado necesita: **un agente autónomo que erradica el toil y estabiliza infraestructuras a escala sobrehumana.**

### Tu ventaja competitiva como arquitecto

Ya tienes tres proyectos production-grade encima (RAG Enterprise, Multi-Agent con LangGraph, AutoDocTranslate con 17K€ de ahorro documentado). Sentinel es el **salto de senior a staff-level thinking**. Los hiring managers buscan exactamente esto: alguien que diseña sistemas "operables por IA" con telemetría limpia, patrones de rollback robustos y razonamiento causal, no probabilístico.

### El reto técnico real (que debes abrazar, no temer)

Sentinel tiene tres tensiones fundamentales que lo hacen difícil — y por eso valioso:

1. **Autonomía vs. Seguridad**: El agente debe actuar rápido, pero no puede tener acceso root sin control
2. **Velocidad vs. Explicabilidad**: Debe resolver en segundos, pero los CISOs necesitan audit trail completo
3. **Generalidad vs. Precisión**: RAG sobre código evoluciona más rápido que la documentación

Tu trabajo no es eliminar estas tensiones. Es diseñar la arquitectura que las gestiona.

### Mentalidad para el sprint que viene

- **No eres el coder, eres el arquitecto.** Diriges a Claude Code y Gemini como si fueran dos ingenieros senior de tu equipo.
- **La fase 1 que ya tienes es el cimiento.** Todo lo que construirás encima debe poder referenciarla.
- **Cada sesión de trabajo tiene un output medible.** No "avancé en Sentinel", sino "implementé el health-check loop del observability agent".
- **Los errores son post-mortems, no fracasos.** El documento de viabilidad que escribiste ya lo dice: los hiring managers quieren ver cómo se comporta el sistema cuando falla.

---

## ⚙️ ARQUITECTURA DE COORDINACIÓN DUAL-LLM

### División de responsabilidades

```
CLAUDE CODE (Antigravity - Terminal)          GEMINI 2.5 PRO (Agent Bar)
─────────────────────────────────────         ─────────────────────────────
✅ Implementación de código Python            ✅ Investigación y diseño de alto nivel
✅ Arquitectura de archivos y módulos         ✅ Análisis de librerías y trade-offs
✅ Debugging y tests unitarios                ✅ Generación de diagramas y docs
✅ Integración con APIs (Prometheus,          ✅ Revisión de arquitectura completa
   Grafana, PagerDuty, etc.)                 ✅ Propuestas de soluciones alternativas
✅ Ejecución de comandos en terminal          ✅ Búsqueda de patrones en HN/Reddit
✅ Git commits y estructura de proyecto       ✅ Validación de decisiones de diseño
✅ Refactoring y optimización                 ✅ Documentación técnica extensa
```

### Protocolo de sincronización

El riesgo principal del dual-LLM es que cada uno tome decisiones arquitectónicas contradictorias. Para evitarlo:

1. **Gemini diseña → Claude implementa** (nunca al revés sin consenso tuyo)
2. **Tú eres el árbitro.** Si hay conflicto entre lo que propone Gemini y lo que Claude genera, TÚ decides.
3. **Contexto compartido vía archivo `SENTINEL_CONTEXT.md`** en la raíz del proyecto. Ambos LLMs lo leerán al inicio de cada sesión.
4. **Cada módulo tiene un "owner"**: cuando Claude Code crea un archivo, inmediatamente se documenta en el contexto compartido.

---

## 📋 PROMPT INICIAL — CLAUDE CODE (Antigravity)

> Copia y pega este prompt exactamente en la terminal de Claude Code al iniciar:

```
# SENTINEL PROJECT — Claude Code Session Initialization

You are the Lead Implementation Engineer for SENTINEL, an Autonomous AI DevOps & SRE Agent. 
I am the architect. You implement what I design.

## Project Context
SENTINEL is a production-grade autonomous agent that:
- Monitors infrastructure via Prometheus/Grafana metrics and logs
- Detects anomalies using LLM-powered root cause analysis
- Executes remediations autonomously (low-risk) or with human approval (high-risk)
- Maintains a complete audit trail of every decision and action
- Integrates with PagerDuty/Slack for incident management

## Current State
Phase 1 is already built. Before anything else, read ALL existing files in the project:
1. Map the complete file structure
2. Read every Python file and understand what's implemented
3. Identify what's missing vs. what Phase 1 doc specifies
4. Create a file called `CLAUDE_STATUS.md` with:
   - Complete file tree with one-line description per file
   - What Phase 1 promises vs. what's actually implemented
   - List of broken imports, missing dependencies, or TODO items
   - Your assessment of code quality issues (max 5 most critical)

## Your Working Principles
- ALWAYS read existing code before writing new code
- NEVER break what's already working
- Write modular, testable code with clear separation of concerns
- Every function must have a docstring explaining what it does and why
- Use type hints everywhere
- When in doubt about architecture, ask me before implementing
- Keep a running `IMPLEMENTATION_LOG.md` updated after each significant change

## Tech Stack Constraints
- Python 3.11+
- FastAPI for any web endpoints
- LangGraph for agent orchestration
- LangChain for LLM integration
- Prometheus client for metrics ingestion
- Pydantic v2 for data models
- Use Claude API (claude-sonnet-4-5 or latest) as the primary LLM brain
- PostgreSQL via SQLAlchemy for persistent state
- Redis for real-time event streaming

## First Task
Start with the audit described above. Output CLAUDE_STATUS.md, then wait for my next instruction.
Do not start implementing anything new until the audit is complete.
```

---

## 📋 PROMPT INICIAL — GEMINI 2.5 PRO (Agent Bar)

> Copia y pega este prompt en la barra de agentes de Gemini:

```
# SENTINEL PROJECT — Gemini Architecture Session Initialization

You are the Senior Architecture Advisor for SENTINEL, an Autonomous AI DevOps & SRE Agent 
that I am building as a production-grade portfolio project and potential commercial product.

## What SENTINEL Does
SENTINEL is an autonomous agent system that:
- Ingests observability data (Prometheus metrics, Grafana logs, traces)
- Performs LLM-powered root cause analysis using causal reasoning (not just pattern matching)
- Classifies remediations by risk level (autonomous vs. human-approved)
- Executes low-risk remediations autonomously (pod restarts, scaling, cache flush)
- Escalates high-risk actions (firewall changes, DB modifications) for human approval
- Maintains complete audit trail for SOC2/compliance requirements
- Integrates with PagerDuty and Slack for incident lifecycle management

## Market Context (for your architectural decisions)
- AIOps market: $303B by 2035, CAGR 22.95%
- Downtime cost in banking/telecom: $5,000+/minute
- 81% of executives trust AI agents to act during crises IF there's explainability
- Primary competition: Datadog AI, PagerDuty AI, Azure SRE Agent
- Differentiation: causal reasoning > probabilistic correlation + full explainability

## Phase 1 Already Built
The first phase is implemented. I need you to:

1. **Research the current state of production SRE agents (2025)**:
   - What are Azure SRE Agent, Rootly AI, and PagerDuty Copilot actually doing?
   - What architectural patterns are emerging as best practices?
   - What are the biggest failure modes teams are reporting on HN/Reddit?

2. **Design the complete SENTINEL architecture** for all phases:
   - Draw a detailed component diagram (use ASCII or Mermaid notation)
   - Define the agent graph (nodes, edges, conditional routing)
   - Specify the data models for: incidents, remediations, audit logs
   - Define the tool inventory (what tools does the agent have access to?)
   - Specify the guardrails system (how do we prevent catastrophic actions?)

3. **Identify the 3 highest-risk architectural decisions** in this project:
   - What could cause the agent to take a wrong action in production?
   - How do we implement "minimum privilege" for the agent's IAM/permissions?
   - How do we handle LLM hallucinations in a production remediation context?

4. **Output a structured architecture document** in Markdown with:
   - System overview diagram
   - Component breakdown with responsibilities
   - Agent graph specification
   - Risk mitigation strategies
   - Recommended implementation order for remaining phases

## Your Role Going Forward
- You research, analyze, and design. A separate implementation agent (Claude Code) builds.
- When I share Claude Code's output with you, review it for architectural consistency
- Flag any implementation choices that deviate from the designed architecture
- Propose alternatives when you identify better approaches

Start with the research and architecture document now.
```

---

## 🔄 PROTOCOLO DE SESIÓN DIARIA

### Al inicio de cada sesión de trabajo:

**Para Claude Code:**
```
Read CLAUDE_STATUS.md and IMPLEMENTATION_LOG.md. 
Today's goal: [SPECIFY YOUR GOAL].
Current phase: [PHASE X].
Constraints: [any time/complexity constraints].
Start by showing me the current state of [specific module].
```

**Para Gemini:**
```
Review the architecture document you created. 
Claude Code has implemented: [paste IMPLEMENTATION_LOG summary].
Question/Decision needed: [your specific architectural question].
```

### Archivo `SENTINEL_CONTEXT.md` (crear en raíz del proyecto)

Actualiza este archivo después de cada sesión. Es el "cerebro compartido":

```markdown
# SENTINEL — Shared Context (Updated: [DATE])

## Phase 1 Status: [COMPLETE/IN_PROGRESS]
- [x] Item 1
- [ ] Item 2

## Current Phase: [X]
## Current Focus: [MODULE/FEATURE]

## Architecture Decisions Locked
1. [Decision]: [Rationale]
2. ...

## Pending Architectural Decisions
1. [Question]: [Options being considered]

## File Ownership
| File | Owner | Status | Description |
|------|-------|--------|-------------|
| agents/orchestrator.py | Claude Code | ✅ Done | Main LangGraph orchestrator |

## Known Issues
1. [Issue]: [Workaround if any]

## Next Session Goals
1. ...
```

---

## 🚨 GUARDRAILS PARA TI (el arquitecto)

1. **Nunca dejes que Claude Code refactorice un módulo que funciona sin revisar primero qué rompe**
2. **Si Gemini propone algo que Claude Code no puede implementar en 2-3 horas, es demasiado complejo para ahora** — simplifica
3. **Commit al final de cada sesión**, aunque sea WIP. Git es tu red de seguridad
4. **El audit trail del agente se implementa desde el día 1**, no al final
5. **Testea cada herramienta del agente de forma aislada** antes de conectarla al grafo principal

---

## 💡 EL INSIGHT MÁS IMPORTANTE

El documento de viabilidad que escribiste lo dice claramente: los hiring managers en HN/Reddit son escépticos de proyectos de IA que son "meros envoltorios de APIs de OpenAI."

**Lo que diferenciará a Sentinel:**
1. **Razonamiento causal**, no solo correlación probabilística
2. **Guardrails auditables**: cada decisión del agente tiene un "¿por qué?" registrado
3. **Métricas reales de impacto**: MTTR antes vs. después, incidentes resueltos autónomamente, falsos positivos
4. **Arquitectura de mínimo privilegio**: el agente solo tiene los permisos que necesita, cuando los necesita

Eso es lo que construiremos. Empieza con el audit de Phase 1 y en la próxima sesión ya tenemos el roadmap completo de fases.

**Let's build something real.**
