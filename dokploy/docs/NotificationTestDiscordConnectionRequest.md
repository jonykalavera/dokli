# NotificationTestDiscordConnectionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**webhook_url** | **str** |  | 

## Example

```python
from openapi_client.models.notification_test_discord_connection_request import NotificationTestDiscordConnectionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationTestDiscordConnectionRequest from a JSON string
notification_test_discord_connection_request_instance = NotificationTestDiscordConnectionRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationTestDiscordConnectionRequest.to_json())

# convert the object into a dict
notification_test_discord_connection_request_dict = notification_test_discord_connection_request_instance.to_dict()
# create an instance of NotificationTestDiscordConnectionRequest from a dict
notification_test_discord_connection_request_from_dict = NotificationTestDiscordConnectionRequest.from_dict(notification_test_discord_connection_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


