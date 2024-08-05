
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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing_extensions import Self


class CertificatesCreateRequest(BaseModel):
    """CertificatesCreateRequest
    """  # noqa: E501

    certificate_id: StrictStr | None = Field(default=None, alias="certificateId")
    name: Annotated[str, Field(min_length=1, strict=True)]
    certificate_data: Annotated[str, Field(min_length=1, strict=True)] = Field(alias="certificateData")
    private_key: Annotated[str, Field(min_length=1, strict=True)] = Field(alias="privateKey")
    certificate_path: StrictStr | None = Field(default=None, alias="certificatePath")
    auto_renew: StrictBool | None = Field(default=None, alias="autoRenew")
    __properties: ClassVar[list[str]] = [
        "certificateId",
        "name",
        "certificateData",
        "privateKey",
        "certificatePath",
        "autoRenew",
    ]

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
        """Create an instance of CertificatesCreateRequest from a JSON string"""
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
        # set to None if auto_renew (nullable) is None
        # and model_fields_set contains the field
        if self.auto_renew is None and "auto_renew" in self.model_fields_set:
            _dict["autoRenew"] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict[str, Any] | None) -> Self | None:
        """Create an instance of CertificatesCreateRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "certificateId": obj.get("certificateId"),
                "name": obj.get("name"),
                "certificateData": obj.get("certificateData"),
                "privateKey": obj.get("privateKey"),
                "certificatePath": obj.get("certificatePath"),
                "autoRenew": obj.get("autoRenew"),
            }
        )
        return _obj