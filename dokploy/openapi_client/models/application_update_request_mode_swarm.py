
"""Dokploy API

Endpoints for dokploy

The version of the OpenAPI document: v0.6.1
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

from __future__ import annotations

import json
import pprint
import re  # noqa: F401
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from openapi_client.models.application_update_request_mode_swarm_replicated import (
    ApplicationUpdateRequestModeSwarmReplicated,
)
from openapi_client.models.application_update_request_mode_swarm_replicated_job import (
    ApplicationUpdateRequestModeSwarmReplicatedJob,
)


class ApplicationUpdateRequestModeSwarm(BaseModel):
    """ApplicationUpdateRequestModeSwarm
    """  # noqa: E501

    replicated: ApplicationUpdateRequestModeSwarmReplicated | None = Field(default=None, alias="Replicated")
    var_global: dict[str, Any] | None = Field(default=None, alias="Global")
    replicated_job: ApplicationUpdateRequestModeSwarmReplicatedJob | None = Field(
        default=None, alias="ReplicatedJob"
    )
    global_job: dict[str, Any] | None = Field(default=None, alias="GlobalJob")
    __properties: ClassVar[list[str]] = ["Replicated", "Global", "ReplicatedJob", "GlobalJob"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self | None:
        """Create an instance of ApplicationUpdateRequestModeSwarm from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of replicated
        if self.replicated:
            _dict["Replicated"] = self.replicated.to_dict()
        # override the default output from pydantic by calling `to_dict()` of replicated_job
        if self.replicated_job:
            _dict["ReplicatedJob"] = self.replicated_job.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict[str, Any] | None) -> Self | None:
        """Create an instance of ApplicationUpdateRequestModeSwarm from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "Replicated": ApplicationUpdateRequestModeSwarmReplicated.from_dict(obj["Replicated"])
                if obj.get("Replicated") is not None
                else None,
                "Global": obj.get("Global"),
                "ReplicatedJob": ApplicationUpdateRequestModeSwarmReplicatedJob.from_dict(obj["ReplicatedJob"])
                if obj.get("ReplicatedJob") is not None
                else None,
                "GlobalJob": obj.get("GlobalJob"),
            }
        )
        return _obj
