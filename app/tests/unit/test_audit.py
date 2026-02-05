import pytest
import os
import json
from app.modules.audit.service import AuditService
from app.core.entities import AuditLog

@pytest.mark.asyncio
async def test_audit_log_creation():
    test_file = "test_audit.log"
    service = AuditService(file_path=test_file)
    
    log = AuditLog(
        component="Test",
        event="TestEvent",
        details={"foo": "bar"}
    )
    
    await service.log_event(log)
    
    assert os.path.exists(test_file)
    
    with open(test_file, 'r') as f:
        line = f.readline()
        data = json.loads(line)
        assert data["component"] == "Test"
        assert data["details"]["foo"] == "bar"
        
    os.remove(test_file)
