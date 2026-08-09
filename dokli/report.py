"""Apply report models."""

from typing import Literal

from pydantic import BaseModel, Field


class ApplyAction(BaseModel):
    """A single apply action."""

    action: Literal["create", "update", "validate", "delete", "skip"]
    kind: str
    project: str = ""
    name: str
    details: str = ""


class ApplyReport(BaseModel):
    """Report of what apply did or would do."""

    actions: list[ApplyAction] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
