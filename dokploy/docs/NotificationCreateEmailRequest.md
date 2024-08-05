# NotificationCreateEmailRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_build_error** | **bool** |  | 
**database_backup** | **bool** |  | 
**dokploy_restart** | **bool** |  | 
**name** | **str** |  | 
**app_deploy** | **bool** |  | 
**docker_cleanup** | **bool** |  | 
**smtp_server** | **str** |  | 
**smtp_port** | **float** |  | 
**username** | **str** |  | 
**password** | **str** |  | 
**from_address** | **str** |  | 
**to_addresses** | **List[str]** |  | 

## Example

```python
from openapi_client.models.notification_create_email_request import NotificationCreateEmailRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationCreateEmailRequest from a JSON string
notification_create_email_request_instance = NotificationCreateEmailRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationCreateEmailRequest.to_json())

# convert the object into a dict
notification_create_email_request_dict = notification_create_email_request_instance.to_dict()
# create an instance of NotificationCreateEmailRequest from a dict
notification_create_email_request_from_dict = NotificationCreateEmailRequest.from_dict(notification_create_email_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

