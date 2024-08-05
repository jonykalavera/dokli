# NotificationRemoveRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**notification_id** | **str** |  | 

## Example

```python
from openapi_client.models.notification_remove_request import NotificationRemoveRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationRemoveRequest from a JSON string
notification_remove_request_instance = NotificationRemoveRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationRemoveRequest.to_json())

# convert the object into a dict
notification_remove_request_dict = notification_remove_request_instance.to_dict()
# create an instance of NotificationRemoveRequest from a dict
notification_remove_request_from_dict = NotificationRemoveRequest.from_dict(notification_remove_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


