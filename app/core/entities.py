from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
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
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: AlertSeverity
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Diagnosis(BaseModel):
    alert_id: str
    root_cause: str
    confidence: float
    suggested_actions: List[ActionType]

class RemediationPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    diagnosis: Diagnosis
    action_type: ActionType
    risk_level: RiskLevel
    requires_approval: bool
    status: str = "PENDING"  # PENDING, APPROVED, EXECUTED, FAILED
    
class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    component: str
    event: str
    details: Dict[str, Any]
