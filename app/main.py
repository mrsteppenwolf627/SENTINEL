import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from typing import List

from .core.config import settings
from .core.logging import logger
from .core.entities import Alert, AuditLog
from .modules.ingestion import AlertSimulator
from .modules.analysis import RuleBasedAnalyzer
from .modules.policy import RiskEvaluator
from .modules.action import ActionExecutor
from .modules.audit import AuditService

# Initialize Modules
simulator = AlertSimulator()
analyzer = RuleBasedAnalyzer()
risk_evaluator = RiskEvaluator()
executor = ActionExecutor()
audit_service = AuditService()

async def processing_loop():
    """Background task to process alerts from the simulator."""
    logger.info("Starting processing loop...")
    async for alert in simulator.get_alerts():
        await process_alert(alert)

async def process_alert(alert: Alert):
    """
    Main Logic Flow: Ingest -> Analyze -> Policy -> Action -> Audit
    """
    try:
        # 0. Log Ingestion
        logger.info(f"Received alert: {alert.source}", extra={"alert_id": alert.id})
        
        # 1. Analyze
        diagnosis = await analyzer.analyze(alert)
        
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
                "alert": alert.model_dump(mode='json'),
                "diagnosis": diagnosis.model_dump(mode='json'),
                "plan": plan.model_dump(mode='json'),
                "result": result
            }
        )
        await audit_service.log_event(log_entry)
        
    except Exception as e:
        logger.error(f"Error processing alert: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run loop in background
    task = asyncio.create_task(processing_loop())
    yield
    # Shutdown
    simulator._running = False
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Processing loop stopped")

app = FastAPI(title="Sentinel", lifespan=lifespan)

@app.get("/")
async def root():
    return {
        "status": "online", 
        "modules": ["Ingestion", "Analysis", "Policy", "Action", "Audit"],
        "docs": "/docs"
    }

@app.get("/audit", response_class=HTMLResponse)
async def view_audit_log():
    """Simple UI to view last 50 audit logs."""
    logs = []
    try:
        with open(settings.AUDIT_FILE_PATH, "r") as f:
            lines = f.readlines()
            # Parse last 50 lines reversed
            for line in reversed(lines[-50:]):
                try:
                    logs.append(dict(json_line=line)) # Simply keep as string for now or parse
                except: pass
    except FileNotFoundError:
        pass
    
    html_content = """
    <html>
        <head>
            <title>Sentinel Audit Log</title>
            <style>
                body { font-family: monospace; background: #1e1e1e; color: #0f0; padding: 20px; }
                .log { border-bottom: 1px solid #333; padding: 5px; }
            </style>
        </head>
        <body>
            <h1>Sentinel Live Audit Trail</h1>
            %s
        </body>
    </html>
    """
    
    log_html = "".join([f"<div class='log'>{l['json_line']}</div>" for l in logs])
    return html_content % log_html

@app.post("/simulate")
async def trigger_simulation(alert: Alert, background_tasks: BackgroundTasks):
    """Manually inject an alert."""
    background_tasks.add_task(process_alert, alert)
    return {"message": "Alert injected"}
