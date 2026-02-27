from collections import defaultdict
from typing import List, Optional, Callable
from ...core.entities import Alert, Diagnosis, ActionType

class Rule:
    def __init__(
        self, 
        name: str, 
        condition: Callable[[Alert], bool], 
        root_cause_template: str,
        suggested_actions: List[ActionType]
    ):
        self.name = name
        self.condition = condition
        self.root_cause_template = root_cause_template
        self.suggested_actions = suggested_actions

    def match(self, alert: Alert) -> bool:
        return self.condition(alert)

    def create_diagnosis(self, alert: Alert) -> Diagnosis:
        # Use a defaultdict so missing metadata keys render as "N/A" instead of raising KeyError.
        safe_metadata = defaultdict(lambda: "N/A", alert.metadata)
        return Diagnosis(
            alert_id=alert.id,
            root_cause=self.root_cause_template.format_map(safe_metadata),
            confidence=1.0,  # Rules are deterministic in this MVP
            suggested_actions=self.suggested_actions
        )

# Pre-defined rules library
COMMON_RULES = [
    Rule(
        name="High CPU",
        condition=lambda a: "cpu" in a.message.lower(),
        root_cause_template="CPU saturation on {component} at {cpu_usage}%",
        suggested_actions=[ActionType.SCALE_UP, ActionType.RESTART_SERVICE]
    ),
    Rule(
        name="Memory Leak",
        condition=lambda a: "memory" in a.message.lower(),
        root_cause_template="Memory leak detected in {component}",
        suggested_actions=[ActionType.RESTART_SERVICE]
    ),
    Rule(
        name="Disk Space",
        condition=lambda a: "disk" in a.message.lower() or "space" in a.message.lower(),
        root_cause_template="Disk {mount} nearly full",
        suggested_actions=[ActionType.CLEAR_CACHE, ActionType.NOTIFICATION]
    ),
    Rule(
        name="DB Connection",
        condition=lambda a: "connection" in a.message.lower(),
        root_cause_template="Database unavailable (Code {error_code})",
        suggested_actions=[ActionType.RESTART_SERVICE, ActionType.MANUAL_INTERVENTION]
    )
]
