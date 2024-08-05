
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
from typing import Annotated, Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr, field_validator
from typing_extensions import Self


class PortCreateRequest(BaseModel):
    """PortCreateRequest
    """  # noqa: E501

    published_port: StrictFloat | StrictInt = Field(alias="publishedPort")
    target_port: StrictFloat | StrictInt = Field(alias="targetPort")
    protocol: StrictStr | None = "tcp"
    application_id: Annotated[str, Field(min_length=1, strict=True)] = Field(alias="applicationId")
    __properties: ClassVar[list[str]] = ["publishedPort", "targetPort", "protocol", "applicationId"]

    @field_validator("protocol")
    def protocol_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(["tcp", "udp"]):
            raise ValueError("must be one of enum values ('tcp', 'udp')")
        return value

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
        """Create an instance of PortCreateRequest from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: dict[str, Any] | None) -> Self | None:
        """Create an instance of PortCreateRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "publishedPort": obj.get("publishedPort"),
                "targetPort": obj.get("targetPort"),
                "protocol": obj.get("protocol") if obj.get("protocol") is not None else "tcp",
                "applicationId": obj.get("applicationId"),
            }
        )
        return _obj