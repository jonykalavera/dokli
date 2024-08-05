# NotificationTestEmailConnectionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**smtp_server** | **str** |  | 
**smtp_port** | **float** |  | 
**username** | **str** |  | 
**password** | **str** |  | 
**to_addresses** | **List[str]** |  | 
**from_address** | **str** |  | 

## Example

```python
from openapi_client.models.notification_test_email_connection_request import NotificationTestEmailConnectionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationTestEmailConnectionRequest from a JSON string
notification_test_email_connection_request_instance = NotificationTestEmailConnectionRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationTestEmailConnectionRequest.to_json())

# convert the object into a dict
notification_test_email_connection_request_dict = notification_test_email_connection_request_instance.to_dict()
# create an instance of NotificationTestEmailConnectionRequest from a dict
notification_test_email_connection_request_from_dict = NotificationTestEmailConnectionRequest.from_dict(notification_test_email_connection_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


