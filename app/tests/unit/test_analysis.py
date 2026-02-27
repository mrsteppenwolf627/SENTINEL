import pytest
from app.modules.analysis.engine import RuleBasedAnalyzer
from app.core.entities import Alert, AlertSeverity, ActionType, EnrichedContext


@pytest.mark.asyncio
async def test_rule_cpu_match():
    analyzer = RuleBasedAnalyzer()
    alert = Alert(
        source="server-01",
        severity=AlertSeverity.CRITICAL,
        message="High CPU usage detected",
        metadata={"cpu_usage": 99, "component": "cpu"},
    )
    context = EnrichedContext(alert=alert)

    diagnosis = await analyzer.analyze(context)

    assert diagnosis.root_cause == "CPU saturation on cpu at 99%"
    assert ActionType.SCALE_UP in diagnosis.suggested_actions


@pytest.mark.asyncio
async def test_rule_no_match():
    analyzer = RuleBasedAnalyzer()
    alert = Alert(
        source="unknown",
        severity=AlertSeverity.INFO,
        message="Something weird happened",
        metadata={},
    )
    context = EnrichedContext(alert=alert)

    diagnosis = await analyzer.analyze(context)

    assert diagnosis.root_cause == "Unknown Anomaly"
    assert diagnosis.confidence == 0.0
