from abc import ABC, abstractmethod
from typing import List, AsyncIterator
from .entities import Alert, Diagnosis, RemediationPlan, AuditLog, ActionType, RiskLevel, EnrichedContext

class IIngestionModule(ABC):
    """Interface for Ingestion Modules (e.g., Simulator, Webhook API)."""
    
    @abstractmethod
    async def get_alerts(self) -> AsyncIterator[Alert]:
        """Stream of incoming alerts."""
        pass

class IAnalysisModule(ABC):
    """Interface for RCA Analysis (e.g., Rule Engine, LLM)."""

    @abstractmethod
    async def analyze(self, context: EnrichedContext) -> Diagnosis:
        """Analyze an enriched context and produce a diagnosis."""
        pass

class IPolicyModule(ABC):
    """Interface for Risk Policy (e.g., Static Rules, ML Risk Model)."""
    
    @abstractmethod
    async def evaluate_risk(self, diagnosis: Diagnosis) -> RemediationPlan:
        """Evaluate risk and create a remediation plan."""
        pass

class IActionModule(ABC):
    """Interface for Action Execution (e.g., SSH, K8s, Mock)."""
    
    @abstractmethod
    async def execute_action(self, plan: RemediationPlan) -> bool:
        """Execute the remediation plan. Returns success/failure."""
        pass

class IAuditModule(ABC):
    """Interface for Audit Logging."""
    
    @abstractmethod
    async def log_event(self, log: AuditLog):
        """Persist an audit log."""
        pass
