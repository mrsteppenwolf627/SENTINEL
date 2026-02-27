# CLAUDE_STATUS.md — Sentinel Codebase Audit
**Generated:** 2026-02-27
**Auditor:** Claude (Lead Implementation Engineer)
**Basis:** Full read of all source files + test run

---

## 1. Complete File Tree

```
Sentinel/
├── app/
│   ├── __init__.py                   # App package marker (empty)
│   ├── main.py                       # FastAPI entry point; background processing loop;
│   │                                 #   /audit HTML viewer; /simulate POST endpoint
│   ├── core/
│   │   ├── __init__.py               # Core package marker (comment only)
│   │   ├── config.py                 # Pydantic-Settings config (env, log level, paths, flags)
│   │   ├── entities.py               # Domain models: Alert, Diagnosis, RemediationPlan, AuditLog
│   │   ├── interfaces.py             # ABCs: IIngestionModule, IAnalysisModule, IPolicyModule,
│   │   │                             #   IActionModule, IAuditModule
│   │   └── logging.py                # Structured JSON logger via python-json-logger
│   ├── modules/
│   │   ├── ingestion/
│   │   │   ├── __init__.py           # Exports AlertSimulator
│   │   │   └── simulator.py          # AlertSimulator: generates 5 hard-coded alert scenarios
│   │   │                             #   at 5s intervals, 70% trigger probability
│   │   ├── analysis/
│   │   │   ├── __init__.py           # Exports RuleBasedAnalyzer
│   │   │   ├── engine.py             # RuleBasedAnalyzer: iterates COMMON_RULES, returns Diagnosis
│   │   │   └── rules.py              # Rule dataclass + COMMON_RULES (4 rules: CPU, Memory,
│   │   │                             #   Disk, DB Connection)
│   │   ├── policy/
│   │   │   ├── __init__.py           # Exports RiskEvaluator
│   │   │   └── risk_manager.py       # RiskEvaluator: maps ActionType → RiskLevel → requires_approval
│   │   ├── action/
│   │   │   ├── __init__.py           # Exports ActionExecutor
│   │   │   └── executors.py          # ActionExecutor: mocked execution (logs only, 1s sleep)
│   │   └── audit/
│   │       ├── __init__.py           # Exports AuditService
│   │       └── service.py            # AuditService: async JSONL append to audit.log
│   └── tests/
│       ├── __init__.py               # Test package marker
│       └── unit/
│           ├── __init__.py           # Unit test package marker
│           ├── test_analysis.py      # 2 tests: CPU rule match, no-match fallback
│           └── test_audit.py         # 1 test: writes and verifies JSONL audit log entry
├── .gitignore
├── audit.log                         # Runtime output — JSONL append log of all decisions
├── PROJECT_CONTEXT.md                # Persistent session memory for AI agents
├── README.md                         # User-facing quick-start guide (Spanish)
├── requirements.txt                  # 9 direct Python dependencies
├── RESUMEN_PROYECTO.md               # (untracked) Project summary document
├── SENTINEL_DOCUMENTATION.md         # Technical architecture doc (Spanish)
└── SENTINEL_Launch_Guide.md          # (untracked) Deployment guide
```

---

## 2. Phase 1 Promises vs. What Is Actually Implemented

| Feature | Promised | Implemented | Notes |
|---|---|---|---|
| Folder structure + Git | ✅ | ✅ | Clean modular layout |
| Structured JSON logging | ✅ | ✅ | python-json-logger, minor deprecation (see Issues) |
| Alert Simulation (CPU/Memory/Disk) | ✅ | ✅ | 5 scenarios, async generator |
| Rule-Based Analyzer | ✅ | ✅ | 4 rules; deterministic |
| Risk Policy (Safe/Moderate/Critical) | ✅ | ✅ | RISK_MAPPING dict in RiskEvaluator |
| Mocked Action Executor | ✅ | ✅ | Logs actions, simulates 1s delay |
| Audit Trail (JSONL file) | ✅ | ✅ | aiofiles async append |
| Async Background Loop | ✅ | ✅ | asyncio.create_task in lifespan |
| HTML Audit Viewer (`/audit`) | ✅ | ⚠️ PARTIAL | Renders but JSON is never parsed (see Issue #1) |
| Manual Inject Endpoint (`/simulate`) | ✅ | ✅ | POST /simulate works |
| Unit Tests | ✅ | ✅ | 3/3 passing |
| Documentation | ✅ | ✅ | README + SENTINEL_DOCUMENTATION.md |

**Phase 1 (as defined in the project docs) is ~95% complete.** The only partial item is the `/audit` viewer which has a bug.

### What Phase 2 (and the session's tech stack spec) requires — NOT YET IMPLEMENTED:

| Capability | Status |
|---|---|
| LLM-based Root Cause Analysis (LangChain + Claude API) | ❌ Not started |
| LangGraph agent orchestration | ❌ Not started |
| PostgreSQL / SQLAlchemy persistence | ❌ Not started (file-based only) |
| Redis event streaming | ❌ Not started |
| Prometheus client / real metrics ingestion | ❌ Not started |
| Webhook ingestion endpoint (Prometheus/Grafana alerts) | ❌ Not started |
| Human approval workflow (API + UI) | ❌ Not started |
| PagerDuty / Slack integration | ❌ Not started |
| Real action executors (SSH, K8s, AWS) | ❌ Not started |

---

## 3. Broken Imports, Missing Dependencies, and TODOs

### 3a. Broken / Missing Imports

| File | Issue | Severity |
|---|---|---|
| `app/main.py` | `import json` is **missing** but `json_line=line` on line 100 implies intent to parse — when file has actual content this causes a `NameError` on `json` if JSON parsing is attempted | HIGH |

### 3b. Missing Dependencies (in `requirements.txt`)

The following are needed for Phase 2 but absent:

```
# LLM / Agent
langchain>=0.2.0
langchain-anthropic>=0.1.0
langgraph>=0.1.0

# Database
sqlalchemy>=2.0.0
alembic>=1.13.0
asyncpg>=0.29.0          # Async PostgreSQL driver
aiosqlite>=0.20.0        # SQLite for local dev

# Real-time
redis>=5.0.0

# Metrics
prometheus-client>=0.20.0
prometheus-api-client>=0.5.4

# HTTP / Webhooks
httpx>=0.27.0

# Environment
python-dotenv>=1.0.0      # Already covered by pydantic-settings but useful standalone
anthropic>=0.30.0         # Direct Claude API client
```

### 3c. Explicit TODOs / Gaps in Existing Code

| File | Line | Issue |
|---|---|---|
| `app/main.py` | 100 | `dict(json_line=line)` — never actually parses JSON; the `/audit` UI shows raw JSONL strings wrapped in a dict key that isn't rendered |
| `app/modules/action/executors.py` | 35 | Typo: `"Slac/Email sent"` → should be `"Slack/Email sent"` |
| `app/modules/policy/risk_manager.py` | 35 | `AUTO_APPROVE_SAFE_ACTIONS` flag misnamed — it's being used to gate `MODERATE` risk, not `SAFE` (SAFE already auto-approves unconditionally on line 31) |
| `app/core/entities.py` | 46 | `RemediationPlan.status` is `str` with no validation — accepts any string, should be `Literal["PENDING", "APPROVED", "EXECUTED", "FAILED"]` |
| `app/modules/analysis/rules.py` | 21 | `rule.create_diagnosis()` calls `.format(**alert.metadata)` — will raise `KeyError` if an injected alert via `/simulate` is missing required metadata keys for that rule |

---

## 4. Code Quality Issues (Top 5 Critical)

### Issue 1 — `main.py`: Missing `import json` causes silent bug in `/audit` viewer
**File:** `app/main.py:100`
**Problem:** The line `logs.append(dict(json_line=line))` creates `{'json_line': "<raw string>"}`. `json` is never imported. The HTML template then renders the raw JSON string as-is, not formatted. The `try/except pass` hides the error. The viewer technically "works" but shows unformatted data and the design intent (parsing JSON entries) is never executed.
**Fix required:** Add `import json` at the top; replace the line with proper JSON parsing.

---

### Issue 2 — `entities.py`: `datetime.utcnow()` is deprecated in Python 3.12+
**File:** `app/core/entities.py:29,50`
```python
# Current (deprecated):
timestamp: datetime = Field(default_factory=datetime.utcnow)

# Required fix:
from datetime import datetime, timezone
timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```
**Impact:** Generates deprecation warnings in all tests (confirmed in test run). Will break in future Python versions.

---

### Issue 3 — `config.py`: Pydantic V2 deprecated `class Config` pattern
**File:** `app/core/config.py:21`
```python
# Current (Pydantic V1 style, deprecated):
class Config:
    env_file = ".env"

# Required fix (Pydantic V2):
from pydantic import ConfigDict
model_config = ConfigDict(env_file=".env")
```
**Impact:** Deprecation warning in all test runs. Will break in Pydantic V3.

---

### Issue 4 — `rules.py`: `KeyError` risk when metadata keys are missing
**File:** `app/modules/analysis/rules.py:21`
```python
# Unsafe:
root_cause=self.root_cause_template.format(**alert.metadata)
```
If a user POSTs to `/simulate` with an alert that matches the "Disk Space" rule but doesn't provide `mount` in metadata, this raises `KeyError`. The outer `try/except` in `main.py:process_alert` catches it, but it produces a silent failure with no useful audit log entry.
**Fix required:** Wrap with `.format_map(defaultdict(lambda: "N/A", alert.metadata))` or validate metadata keys in the Rule class.

---

### Issue 5 — `risk_manager.py`: Policy flag semantics are misleading
**File:** `app/modules/policy/risk_manager.py:35`
```python
elif risk_level == RiskLevel.MODERATE:
    requires_approval = not settings.AUTO_APPROVE_SAFE_ACTIONS
```
The flag `AUTO_APPROVE_SAFE_ACTIONS` applies to `MODERATE` risk actions (SCALE_UP, RESTART_SERVICE) — not to `SAFE` actions, which are always auto-approved regardless. This naming is confusing and will cause misconfigurations when Phase 2 adds real executors. The flag should be renamed to `AUTO_APPROVE_MODERATE_ACTIONS` or the logic needs a dedicated `AUTO_APPROVE_MODERATE` setting.

---

## 5. Test Coverage Summary

| Test | Status | Covers |
|---|---|---|
| `test_rule_cpu_match` | ✅ PASS | CPU rule matching and Diagnosis fields |
| `test_rule_no_match` | ✅ PASS | Fallback Diagnosis on no rule match |
| `test_audit_log_creation` | ✅ PASS | AuditService writes and reads JSONL |

**Not covered:**
- `RiskEvaluator` (no tests)
- `ActionExecutor` (no tests)
- `AlertSimulator` (no tests)
- `main.py` orchestration / end-to-end (no integration tests)
- Edge cases: missing metadata keys, CRITICAL risk path, PENDING_APPROVAL flow

---

## 6. Environment Notes

- **Python runtime detected:** 3.14.0 (venv) — docs say 3.11+, compatible but newer than expected
- **Pytest-asyncio mode:** STRICT — all async tests require explicit `@pytest.mark.asyncio` decorator (currently correct)
- **`pythonjsonlogger` import path deprecated:** `pythonjsonlogger.jsonlogger` → should be `pythonjsonlogger.json`

---

## 7. Audit Verdict

Phase 1 is **functionally complete and stable** with 3/3 tests passing. The codebase is clean, modular, and well-architected for its scope.

**Before Phase 2 work begins**, I recommend fixing Issues #1 and #4 (the `import json` bug and the `KeyError` risk) as they affect runtime correctness. Issues #2, #3, and #5 are lower priority but should be addressed before production.

**Ready to receive Phase 2 instructions.**
