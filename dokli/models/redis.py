"""Redis service model."""

from datetime import datetime
from typing import Any

import humanize
from pydantic import BaseModel, SecretStr


class RedisService(BaseModel):
    """Redis service model."""

    redisId: str
    name: str
    appName: str
    description: str
    databasePassword: SecretStr
    dockerImage: str
    command: dict[str, Any] | None
    env: dict[str, Any] | None
    memoryReservation: dict[str, Any] | None
    memoryLimit: dict[str, Any] | None
    cpuReservation: dict[str, Any] | None
    cpuLimit: dict[str, Any] | None
    externalPort: dict[str, Any] | None
    createdAt: datetime
    applicationStatus: str
    projectId: str

    @property
    def time_since_created(self) -> str:
        """Time since project created in natural language."""
        return humanize.naturaltime(self.createdAt)
