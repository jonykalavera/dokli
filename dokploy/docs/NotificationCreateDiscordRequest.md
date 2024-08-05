# NotificationCreateDiscordRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_build_error** | **bool** |  | 
**database_backup** | **bool** |  | 
**dokploy_restart** | **bool** |  | 
**name** | **str** |  | 
**app_deploy** | **bool** |  | 
**docker_cleanup** | **bool** |  | 
**webhook_url** | **str** |  | 

## Example

```python
from openapi_client.models.notification_create_discord_request import NotificationCreateDiscordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationCreateDiscordRequest from a JSON string
notification_create_discord_request_instance = NotificationCreateDiscordRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationCreateDiscordRequest.to_json())

# convert the object into a dict
notification_create_discord_request_dict = notification_create_discord_request_instance.to_dict()
# create an instance of NotificationCreateDiscordRequest from a dict
notification_create_discord_request_from_dict = NotificationCreateDiscordRequest.from_dict(notification_create_discord_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


