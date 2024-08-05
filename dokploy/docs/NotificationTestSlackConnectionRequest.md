# NotificationTestSlackConnectionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**webhook_url** | **str** |  | 
**channel** | **str** |  | 

## Example

```python
from openapi_client.models.notification_test_slack_connection_request import NotificationTestSlackConnectionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationTestSlackConnectionRequest from a JSON string
notification_test_slack_connection_request_instance = NotificationTestSlackConnectionRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationTestSlackConnectionRequest.to_json())

# convert the object into a dict
notification_test_slack_connection_request_dict = notification_test_slack_connection_request_instance.to_dict()
# create an instance of NotificationTestSlackConnectionRequest from a dict
notification_test_slack_connection_request_from_dict = NotificationTestSlackConnectionRequest.from_dict(notification_test_slack_connection_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


