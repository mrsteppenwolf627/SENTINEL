from typing import List
from ...core.interfaces import IAnalysisModule
from ...core.entities import Alert, Diagnosis, ActionType
from ...core.logging import logger
from .rules import COMMON_RULES, Rule

class RuleBasedAnalyzer(IAnalysisModule):
    """
    Analyzes alerts using a set of static rules to determine root cause.
    """
    def __init__(self, rules: List[Rule] = None):
        self.rules = rules or COMMON_RULES

    async def analyze(self, alert: Alert) -> Diagnosis:
        for rule in self.rules:
            if rule.match(alert):
                logger.info(f"Alert matched rule: {rule.name}", extra={"alert_id": alert.id})
                return rule.create_diagnosis(alert)
        
        # Fallback if no rule matches
        logger.warning("No rule matched alert", extra={"alert_id": alert.id, "alert_message": alert.message})
        return Diagnosis(
            alert_id=alert.id,
            root_cause="Unknown Anomaly",
            confidence=0.0,
            suggested_actions=[ActionType.MANUAL_INTERVENTION]
        )
