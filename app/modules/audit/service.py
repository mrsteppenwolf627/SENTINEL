import json
import aiofiles
from ...core.interfaces import IAuditModule
from ...core.entities import AuditLog
from ...core.config import settings
from ...core.logging import logger

class AuditService(IAuditModule):
    """
    Persists audit logs to a JSONL file.
    """
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path or settings.AUDIT_FILE_PATH

    async def log_event(self, log: AuditLog):
        try:
            # Append to file asynchronously
            async with aiofiles.open(self.file_path, mode='a') as f:
                entry = log.model_dump(mode='json')
                await f.write(json.dumps(entry) + "\n")
        except Exception as e:
            # Fallback to system logger if file write fails
            logger.error(f"Failed to write audit log: {e}", extra={"audit_id": log.id})
