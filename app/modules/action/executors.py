import asyncio
from ...core.interfaces import IActionModule
from ...core.entities import RemediationPlan, ActionType
from ...core.logging import logger

class ActionExecutor(IActionModule):
    """
    Executes remediation plans. In MVP, this mostly logs the actions.
    """

    async def execute_action(self, plan: RemediationPlan) -> bool:
        if plan.requires_approval and plan.status != "APPROVED":
            logger.warning(
                "Attempted to execute unapproved plan", 
                extra={"plan_id": plan.id, "action": plan.action_type}
            )
            return False

        logger.info(f"Executing action: {plan.action_type}", extra={"plan_id": plan.id})
        
        try:
            # Simulate execution time
            await asyncio.sleep(1)
            
            # Mock Implementation logic
            if plan.action_type == ActionType.RESTART_SERVICE:
                logger.info("Service restarted successfully via SSH (Mock)")
            elif plan.action_type == ActionType.CLEAR_CACHE:
                logger.info("Cache cleared via API (Mock)")
            elif plan.action_type == ActionType.SCALE_UP:
                logger.info("Scaling group updated to +1 instance (Mock)")
            elif plan.action_type == ActionType.BLOCK_IP:
                logger.info("Firewall rule added (Mock)")
            elif plan.action_type == ActionType.NOTIFICATION:
                logger.info("Slac/Email sent (Mock)")
            elif plan.action_type == ActionType.MANUAL_INTERVENTION:
                logger.info("Ticket created in Jira (Mock)")
            
            plan.status = "EXECUTED"
            return True
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}", extra={"plan_id": plan.id})
            plan.status = "FAILED"
            return False
