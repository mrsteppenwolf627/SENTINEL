import pytest
from app.modules.analysis.engine import RuleBasedAnalyzer
from app.core.entities import Alert, AlertSeverity, ActionType

@pytest.mark.asyncio
async def test_rule_cpu_match():
    analyzer = RuleBasedAnalyzer()
    alert = Alert(
        source="server-01", 
        severity=AlertSeverity.CRITICAL,
        message="High CPU usage detected",
        metadata={"cpu_usage": 99, "component": "cpu"}
    )
    
    diagnosis = await analyzer.analyze(alert)
    
    assert diagnosis.root_cause == "CPU saturation on cpu at 99%"
    assert ActionType.SCALE_UP in diagnosis.suggested_actions

@pytest.mark.asyncio
async def test_rule_no_match():
    analyzer = RuleBasedAnalyzer()
    alert = Alert(
        source="unknown", 
        severity=AlertSeverity.INFO,
        message="Something weird happened",
        metadata={}
    )
    
    diagnosis = await analyzer.analyze(alert)
    
    assert diagnosis.root_cause == "Unknown Anomaly"
    assert diagnosis.confidence == 0.0
