
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


class NotificationUpdateTelegramRequest(BaseModel):
    """NotificationUpdateTelegramRequest
    """  # noqa: E501

    app_build_error: StrictBool | None = Field(default=None, alias="appBuildError")
    database_backup: StrictBool | None = Field(default=None, alias="databaseBackup")
    dokploy_restart: StrictBool | None = Field(default=None, alias="dokployRestart")
    name: StrictStr | None = None
    app_deploy: StrictBool | None = Field(default=None, alias="appDeploy")
    docker_cleanup: StrictBool | None = Field(default=None, alias="dockerCleanup")
    bot_token: Annotated[str, Field(min_length=1, strict=True)] | None = Field(default=None, alias="botToken")
    chat_id: Annotated[str, Field(min_length=1, strict=True)] | None = Field(default=None, alias="chatId")
    notification_id: Annotated[str, Field(min_length=1, strict=True)] = Field(alias="notificationId")
    telegram_id: Annotated[str, Field(min_length=1, strict=True)] = Field(alias="telegramId")
    __properties: ClassVar[list[str]] = [
        "appBuildError",
        "databaseBackup",
        "dokployRestart",
        "name",
        "appDeploy",
        "dockerCleanup",
        "botToken",
        "chatId",
        "notificationId",
        "telegramId",
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
        """Create an instance of NotificationUpdateTelegramRequest from a JSON string"""
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
        """Create an instance of NotificationUpdateTelegramRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "appBuildError": obj.get("appBuildError"),
                "databaseBackup": obj.get("databaseBackup"),
                "dokployRestart": obj.get("dokployRestart"),
                "name": obj.get("name"),
                "appDeploy": obj.get("appDeploy"),
                "dockerCleanup": obj.get("dockerCleanup"),
                "botToken": obj.get("botToken"),
                "chatId": obj.get("chatId"),
                "notificationId": obj.get("notificationId"),
                "telegramId": obj.get("telegramId"),
            }
        )
        return _obj