# 🧠 SENTINEL PROJECT CONTEXT

> **⚠️ CRITICAL RULE FOR AI AGENTS:**
> **EVERY TIME YOU PUSH TO GITHUB, YOU MUST UPDATE THIS FILE WITH THE LATEST CHANGES, DECISIONS, AND NEXT STEPS.**
> This file serves as your persistent memory between sessions. Read it FIRST when starting a new session.

---

## 📅 Last Updated
**Date:** 2026-02-05
**Version:** MVP 1.0 (Initial Release)
**Status:** Stable / Released
**Repository:** [https://github.com/mrsteppenwolf627/Sentinel_MPV_V1.git](https://github.com/mrsteppenwolf627/Sentinel_MPV_V1.git)

---

## 📌 Project Overview
**Sentinel** is an autonomous infrastructure agent designed to detect, diagnose, and remediate incidents without human intervention (unless risk is high).

### Current Capabilities (MVP)
1.  **Simulated Ingestion**: Generates fake CPU, Memory, and Disk alerts (`app/modules/ingestion`).
2.  **Rule-Based Analysis**: Maps alerts to diagnoses using static logic (`app/modules/analysis`).
3.  **Risk Policy**: Classifies actions as SAFE (auto) or CRITICAL (approval needed).
4.  **Mocked Execution**: Logs actions instead of executing them (safety first).
5.  **Audit Trail**: Records every decision in `audit.log` (JSONL format).

---

## 🏗️ Technical Architecture State

### Module Map
| Module | Implementation File | Responsibility |
| :--- | :--- | :--- |
| **Core** | `app/core/` | Entities, Interfaces, Config, Logger. |
| **Ingestion** | `app/modules/ingestion/simulator.py` | Generates random `Alert` objects. |
| **Analysis** | `app/modules/analysis/engine.py` | Consumes `Alert`, produces `Diagnosis`. |
| **Policy** | `app/modules/policy/risk_manager.py` | Consumes `Diagnosis`, produces `RemediationPlan`. |
| **Action** | `app/modules/action/executors.py` | Executes `RemediationPlan` (Mocked). |
| **Audit** | `app/modules/audit/service.py` | Persists logs to file. |
| **Main** | `app/main.py` | FastAPI app, background processing loop. |

### Key Design Patterns
- **Dependency Injection**: Modules implement interfaces defined in `app.core.interfaces`.
- **Structured Logging**: All logs use `extra={...}` for JSON parsing.
- **AsyncIO**: The main processing loop is non-blocking.

---

## 📝 Recent Session History (The "Memory")

### Session 1: Genesis & MVP (Feb 5, 2026)
1.  **Initialization**: Created strict folder structure (`app/core`, `app/modules`), initialized Git, and set up Python 3.11+ environment.
2.  **Implementation**: Built all core modules from scratch following the architecture plan.
3.  **Verification**:
    *   Encountered missing `aiofiles` and `pytest-asyncio` -> **SOLVED** (Installed).
    *   Encountered `KeyError` in logger because `message` is a reserved key -> **SOLVED** (Renamed to `alert_message` in `engine.py`).
    *   Verified end-to-end flow with `pytest` and manual simulation.
4.  **Documentation**: Created `SENTINEL_DOCUMENTATION.md` and a user-friendly `README.md`.
5.  **Deployment**: Pushed MVP v1.0 to GitHub `main` branch.

---

## 🛣️ Active Roadmap (Next Steps)

**Immediate Priorities for Next Session:**
1.  [ ] **Persistence Layer**: Migrate `audit.log` to a real database (SQLite for local, Postgres for prod).
2.  [ ] **Smart Analysis**: Replace/Augment `RuleBasedAnalyzer` with an **LLM-based analyzer** (the "Brain").
3.  [ ] **Real Inputs**: Create a Webhook endpoint to receive alerts from *real* tools (Prometheus/Grafana).

**Long-term Vision:**
- SaaS Multi-tenancy.
- React Dashboard.
- Kubernetes Operator.

---

## 🛑 Operational Rules
1.  **Context First**: Always check this file to know where we left off.
2.  **Update on Push**: Never push code without updating "Recent Session History" in this file.
3.  **Modular**: Do not break the Interface segregation.
4.  **Tests**: If you write code, you write tests.
