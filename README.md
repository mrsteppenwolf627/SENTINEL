# Sentinel

**Autonomous Infrastructure Agent**

Sentinel is a modular, autonomous agent designed to detect, diagnose, and remediate infrastructure incidents with configurable risk policies.

## Features (MVP)
- **Ingestion**: Simulates and accepts alerts/logs.
- **Analysis**: Rule-based Root Cause Analysis (RCA).
- **Policy**: Risk assessment for every proposed action.
- **Action**: Execution of remediation steps (Mocked for safety).
- **Audit**: Full traceability of decisions.

## Architecture
Modular design with strict separation of concerns:
- `Core`: Domain entities and interfaces.
- `Modules`: Pluggable components for logic.
- `App`: API and orchestration layer.

## Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest`
3. Start app: `uvicorn app.main:app --reload`
