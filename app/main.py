import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .core.config import settings
from .core.logging import logger
from .core.entities import Alert, AuditLog
from .modules.ingestion import AlertSimulator
from .modules.analysis import RuleBasedAnalyzer, LLMAnalyzer
from .modules.policy import RiskEvaluator
from .modules.action import ActionExecutor
from .modules.audit import AuditService
from .modules.context import ContextBuilderService

# ---------------------------------------------------------------------------
# DB session factory (lazy — only connects on first use)
# ContextBuilderService catches any connection errors gracefully.
# ---------------------------------------------------------------------------
_engine = create_async_engine(settings.DATABASE_URL, echo=False)
_AsyncSessionLocal = async_sessionmaker(_engine, expire_on_commit=False)

# ---------------------------------------------------------------------------
# Module wiring
# ---------------------------------------------------------------------------
simulator = AlertSimulator()
risk_evaluator = RiskEvaluator()
executor = ActionExecutor()
audit_service = AuditService()

context_builder = ContextBuilderService(session_factory=_AsyncSessionLocal)

# Choose analyzer: LLM if API key is set, otherwise rule-based fallback only.
_rule_analyzer = RuleBasedAnalyzer()
if settings.ANTHROPIC_API_KEY:
    analyzer = LLMAnalyzer(
        api_key=settings.ANTHROPIC_API_KEY,
        model=settings.LLM_MODEL,
        fallback_analyzer=_rule_analyzer,
    )
    logger.info("LLM Brain active", extra={"model": settings.LLM_MODEL})
else:
    analyzer = _rule_analyzer
    logger.info("LLM Brain inactive (no ANTHROPIC_API_KEY) — using rule engine")


async def processing_loop():
    """Background task to process alerts from the simulator."""
    logger.info("Starting processing loop...")
    async for alert in simulator.get_alerts():
        await process_alert(alert)


async def process_alert(alert: Alert):
    """
    Main orchestration flow: Ingest → EnrichContext → Analyze → Policy → Action → Audit.
    Any unhandled exception is caught and logged so the loop stays alive.
    """
    try:
        # 0. Log Ingestion
        logger.info(f"Received alert: {alert.source}", extra={"alert_id": alert.id})

        # 0.5 Build enriched context (queries DB for historical incidents/plans)
        context = await context_builder.build(alert)

        # 1. Analyze
        diagnosis = await analyzer.analyze(context)

        # 2. Policy / Risk
        plan = await risk_evaluator.evaluate_risk(diagnosis)

        # 3. Action (if auto-approved)
        if not plan.requires_approval:
            success = await executor.execute_action(plan)
            result = "EXECUTED" if success else "FAILED"
        else:
            result = "PENDING_APPROVAL"
            logger.info("Action requires approval", extra={"plan_id": plan.id})

        # 4. Audit
        log_entry = AuditLog(
            component="Orchestrator",
            event="AlertProcessed",
            details={
                "alert": alert.model_dump(mode="json"),
                "diagnosis": diagnosis.model_dump(mode="json"),
                "plan": plan.model_dump(mode="json"),
                "result": result,
            },
        )
        await audit_service.log_event(log_entry)

    except Exception as e:
        logger.error(f"Error processing alert: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage background processing loop lifecycle with the FastAPI app."""
    task = asyncio.create_task(processing_loop())
    yield
    simulator._running = False
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Processing loop stopped")


app = FastAPI(title="Sentinel", lifespan=lifespan)


@app.get("/")
async def root():
    """Health check endpoint — returns module list and docs link."""
    return {
        "status": "online",
        "analyzer": type(analyzer).__name__,
        "modules": ["Ingestion", "Analysis", "Policy", "Action", "Audit"],
        "docs": "/docs",
    }


@app.get("/audit", response_class=HTMLResponse)
async def view_audit_log():
    """Render the last 50 audit log entries as a formatted HTML page."""
    entries: list[dict] = []
    try:
        with open(settings.AUDIT_FILE_PATH, "r") as f:
            lines = f.readlines()
        for line in reversed(lines[-50:]):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"raw": line})
    except FileNotFoundError:
        pass

    def _render_entry(entry: dict) -> str:
        timestamp = entry.get("timestamp", "")
        component = entry.get("component", "")
        event = entry.get("event", "")
        details = entry.get("details", {})
        result = details.get("result", "")
        alert = details.get("alert", {})
        source = alert.get("source", "")
        severity = alert.get("severity", "")
        message = alert.get("message", "")
        return (
            f"<div class='log'>"
            f"<span class='ts'>{timestamp}</span> "
            f"[<span class='cmp'>{component}</span>] "
            f"<span class='evt'>{event}</span> — "
            f"<span class='src'>{source}</span> "
            f"<span class='sev sev-{severity}'>{severity}</span>: "
            f"{message} → <span class='res'>{result}</span>"
            f"</div>"
        )

    rows = "".join(_render_entry(e) for e in entries) if entries else "<p>No logs yet.</p>"

    html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <title>Sentinel Audit Log</title>
    <style>
      body {{ font-family: monospace; background: #1e1e1e; color: #ccc; padding: 20px; }}
      h1   {{ color: #0f0; }}
      .log {{ border-bottom: 1px solid #333; padding: 6px 2px; }}
      .ts  {{ color: #777; font-size: 0.85em; }}
      .cmp {{ color: #58a6ff; }}
      .evt {{ color: #0f0; font-weight: bold; }}
      .src {{ color: #e6c07b; }}
      .res {{ color: #98c379; font-weight: bold; }}
      .sev {{ padding: 1px 5px; border-radius: 3px; font-size: 0.8em; }}
      .sev-CRITICAL {{ background:#c0392b; color:#fff; }}
      .sev-FATAL    {{ background:#8e44ad; color:#fff; }}
      .sev-WARNING  {{ background:#e67e22; color:#fff; }}
      .sev-INFO     {{ background:#27ae60; color:#fff; }}
    </style>
  </head>
  <body>
    <h1>Sentinel Live Audit Trail</h1>
    {rows}
  </body>
</html>"""
    return html_content


@app.post("/simulate")
async def trigger_simulation(alert: Alert, background_tasks: BackgroundTasks):
    """Manually inject an alert into the processing pipeline."""
    background_tasks.add_task(process_alert, alert)
    return {"message": "Alert injected", "alert_id": alert.id}
