import asyncio
import random
import uuid
from typing import AsyncIterator
from ...core.interfaces import IIngestionModule
from ...core.entities import Alert, AlertSeverity

class AlertSimulator(IIngestionModule):
    """
    Simulates a stream of infrastructure alerts for testing and MVP purposes.
    Generates random CPU, Memory, and Disk events.
    """
    
    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self._running = True

    async def get_alerts(self) -> AsyncIterator[Alert]:
        """Yields simulated alerts at a defined interval."""
        while self._running:
            await asyncio.sleep(self.interval)
            
            # Simulate occasional alerts
            if random.random() < 0.7:  # 70% chance of alert each interval
                yield self._generate_random_alert()

    def _generate_random_alert(self) -> Alert:
        scenarios = [
            {
                "message": "High CPU usage detected (95%)",
                "severity": AlertSeverity.CRITICAL,
                "source": "web-server-01",
                "metadata": {"cpu_usage": 95, "component": "cpu"}
            },
            {
                "message": "Memory leak detected in service",
                "severity": AlertSeverity.WARNING,
                "source": "api-gateway",
                "metadata": {"memory_free": "128MB", "component": "memory"}
            },
            {
                "message": "Disk space low (/var/log)",
                "severity": AlertSeverity.WARNING,
                "source": "db-primary",
                "metadata": {"disk_usage": "92%", "mount": "/var/log"}
            },
            {
                "message": "Service responding slowly (>2s latency)",
                "severity": AlertSeverity.INFO,
                "source": "search-service",
                "metadata": {"latency_ms": 2500}
            },
            {
                "message": "Database connection refused",
                "severity": AlertSeverity.FATAL,
                "source": "inventory-db",
                "metadata": {"error_code": 5003}
            }
        ]
        
        scenario = random.choice(scenarios)
        
        return Alert(
            id=str(uuid.uuid4()),
            source=scenario["source"],
            severity=scenario["severity"],
            message=scenario["message"],
            metadata=scenario["metadata"]
        )
