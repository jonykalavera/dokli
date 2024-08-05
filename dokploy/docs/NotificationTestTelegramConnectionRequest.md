# NotificationTestTelegramConnectionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bot_token** | **str** |  | 
**chat_id** | **str** |  | 

## Example

```python
from openapi_client.models.notification_test_telegram_connection_request import NotificationTestTelegramConnectionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationTestTelegramConnectionRequest from a JSON string
notification_test_telegram_connection_request_instance = NotificationTestTelegramConnectionRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationTestTelegramConnectionRequest.to_json())

# convert the object into a dict
notification_test_telegram_connection_request_dict = notification_test_telegram_connection_request_instance.to_dict()
# create an instance of NotificationTestTelegramConnectionRequest from a dict
notification_test_telegram_connection_request_from_dict = NotificationTestTelegramConnectionRequest.from_dict(notification_test_telegram_connection_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


