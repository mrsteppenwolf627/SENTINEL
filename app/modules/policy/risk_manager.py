from ...core.interfaces import IPolicyModule
from ...core.entities import Diagnosis, RemediationPlan, RiskLevel, ActionType
from ...core.config import settings
from ...core.logging import logger
import uuid

class RiskEvaluator(IPolicyModule):
    """
    Evaluates risk for proposed actions based on configured policies.
    """
    
    RISK_MAPPING = {
        ActionType.NOTIFICATION: RiskLevel.SAFE,
        ActionType.CLEAR_CACHE: RiskLevel.SAFE,
        ActionType.SCALE_UP: RiskLevel.MODERATE,
        ActionType.RESTART_SERVICE: RiskLevel.MODERATE,
        ActionType.BLOCK_IP: RiskLevel.MODERATE,
        ActionType.MANUAL_INTERVENTION: RiskLevel.CRITICAL
    }

    async def evaluate_risk(self, diagnosis: Diagnosis) -> RemediationPlan:
        # Default strategy: Pick the first suggested action
        # In a real system, we might evaluate all and choose the best trade-off
        action_type = diagnosis.suggested_actions[0] if diagnosis.suggested_actions else ActionType.MANUAL_INTERVENTION
        
        risk_level = self.RISK_MAPPING.get(action_type, RiskLevel.CRITICAL)
        
        # Policy Logic
        requires_approval = True
        
        if risk_level == RiskLevel.SAFE:
            requires_approval = False
        elif risk_level == RiskLevel.MODERATE:
            # Check config for auto-approval
            requires_approval = not settings.AUTO_APPROVE_SAFE_ACTIONS
        elif risk_level == RiskLevel.CRITICAL:
            requires_approval = True
            
        logger.info(
            f"Risk evaluated: {risk_level}", 
            extra={
                "diagnosis_id": diagnosis.alert_id, 
                "action": action_type, 
                "requires_approval": requires_approval
            }
        )

        return RemediationPlan(
            id=str(uuid.uuid4()),
            diagnosis=diagnosis,
            action_type=action_type,
            risk_level=risk_level,
            requires_approval=requires_approval,
            status="PENDING"
        )
