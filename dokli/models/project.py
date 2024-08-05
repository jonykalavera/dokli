"""Project model."""

from datetime import datetime
from typing import Any

import humanize
from pydantic import BaseModel


class Project(BaseModel):
    """Dockploy API project."""

    projectId: str
    name: str
    description: str
    createdAt: datetime
    adminId: str
    applications: list[dict[str, Any]]
    mariadb: list[dict[str, Any]]
    mongo: list[dict[str, Any]]
    mysql: list[dict[str, Any]]
    postgres: list[dict[str, Any]]
    redis: list[dict[str, Any]]
    compose: list[dict[str, Any]]

    @property
    def time_since_created(self) -> str:
        """Time since project created in natural language."""
        return humanize.naturaltime(self.createdAt)

    @property
    def services(self) -> list[dict[str, Any]]:
        """Get all services."""
        return self.applications + self.mariadb + self.mongo + self.mysql + self.postgres + self.redis + self.compose
