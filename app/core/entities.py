from enum import Enum
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

class RiskLevel(str, Enum):
    SAFE = "SAFE"
    MODERATE = "MODERATE"
    CRITICAL = "CRITICAL"

class ActionType(str, Enum):
    RESTART_SERVICE = "RESTART_SERVICE"
    CLEAR_CACHE = "CLEAR_CACHE"
    SCALE_UP = "SCALE_UP"
    BLOCK_IP = "BLOCK_IP"
    NOTIFICATION = "NOTIFICATION"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: AlertSeverity
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Diagnosis(BaseModel):
    alert_id: str
    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternative_hypotheses: List[str] = Field(default_factory=list)
    reasoning_trace: str = ""
    suggested_actions: List[ActionType]

class RemediationPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    diagnosis: Diagnosis
    action_type: ActionType
    risk_level: RiskLevel
    requires_approval: bool
    status: Literal["PENDING", "APPROVED", "EXECUTED", "FAILED"] = "PENDING"
    
class Incident(BaseModel):
    """Represents an ongoing or historical incident derived from an alert."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str
    source: str
    severity: AlertSeverity
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["OPEN", "ANALYZING", "MITIGATING", "CLOSED"] = "OPEN"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None

class EnrichedContext(BaseModel):
    """Data object containing the original alert and historical DB context."""
    alert: Alert
    recent_similar_incidents: List[Incident] = Field(default_factory=list)
    past_remediations_for_source: List[RemediationPlan] = Field(default_factory=list)


class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    component: str
    event: str
    details: Dict[str, Any]
