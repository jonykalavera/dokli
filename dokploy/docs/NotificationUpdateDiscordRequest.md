# NotificationUpdateDiscordRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_build_error** | **bool** |  | [optional] 
**database_backup** | **bool** |  | [optional] 
**dokploy_restart** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**app_deploy** | **bool** |  | [optional] 
**docker_cleanup** | **bool** |  | [optional] 
**webhook_url** | **str** |  | [optional] 
**notification_id** | **str** |  | 
**discord_id** | **str** |  | 

## Example

```python
from openapi_client.models.notification_update_discord_request import NotificationUpdateDiscordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationUpdateDiscordRequest from a JSON string
notification_update_discord_request_instance = NotificationUpdateDiscordRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationUpdateDiscordRequest.to_json())

# convert the object into a dict
notification_update_discord_request_dict = notification_update_discord_request_instance.to_dict()
# create an instance of NotificationUpdateDiscordRequest from a dict
notification_update_discord_request_from_dict = NotificationUpdateDiscordRequest.from_dict(notification_update_discord_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


