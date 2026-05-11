from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
import time


class HealthStatus(BaseModel):
    status: Literal["healthy", "degraded", "critical"] = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    uptime_seconds: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_agents: int = 0
    pending_tasks: int = 0
    error_count: int = 0
    warnings: list[str] = Field(default_factory=list)

    def is_healthy(self) -> bool:
        return self.status == "healthy"

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
        if len(self.warnings) > 5:
            self.status = "degraded"


class HeartbeatMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.health_status = HealthStatus()
        self._check_interval = 60
        self._last_check = time.time()

    def beat(self) -> HealthStatus:
        current_time = time.time()
        self.health_status.timestamp = datetime.now()
        self.health_status.uptime_seconds = current_time - self.start_time

        if current_time - self._last_check >= self._check_interval:
            self._perform_health_check()
            self._last_check = current_time

        return self.health_status

    def _perform_health_check(self) -> None:
        self.health_status.warnings.clear()

        try:
            import psutil
            self.health_status.cpu_usage = psutil.cpu_percent() / 100.0
            self.health_status.memory_usage = psutil.virtual_memory().percent / 100.0
        except ImportError:
            self.health_status.cpu_usage = 0.0
            self.health_status.memory_usage = 0.0

        if self.health_status.memory_usage > 0.9:
            self.health_status.add_warning("High memory usage")
            self.health_status.status = "degraded"

        if self.health_status.error_count > 10:
            self.health_status.status = "critical"
            self.health_status.add_warning("High error rate")

    def record_task(self, pending: bool = True) -> None:
        if pending:
            self.health_status.pending_tasks += 1
        else:
            self.health_status.pending_tasks = max(0, self.health_status.pending_tasks - 1)

    def record_error(self) -> None:
        self.health_status.error_count += 1
        if self.health_status.error_count > 5:
            self.health_status.status = "degraded"

    def reset_errors(self) -> None:
        self.health_status.error_count = 0
        if self.health_status.status == "degraded" and len(self.health_status.warnings) < 3:
            self.health_status.status = "healthy"

    def get_report(self) -> str:
        h = self.health_status
        return f"""# Heartbeat Report
Status: {h.status.upper()}
Uptime: {h.uptime_seconds:.0f}s
CPU: {h.cpu_usage:.1%}
Memory: {h.memory_usage:.1%}
Active Agents: {h.active_agents}
Pending Tasks: {h.pending_tasks}
Errors: {h.error_count}
Warnings: {len(h.warnings)}
"""


HEARTBEAT_MONITOR = HeartbeatMonitor()
