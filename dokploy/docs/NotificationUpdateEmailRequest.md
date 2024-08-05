# NotificationUpdateEmailRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_build_error** | **bool** |  | [optional] 
**database_backup** | **bool** |  | [optional] 
**dokploy_restart** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**app_deploy** | **bool** |  | [optional] 
**docker_cleanup** | **bool** |  | [optional] 
**smtp_server** | **str** |  | [optional] 
**smtp_port** | **float** |  | [optional] 
**username** | **str** |  | [optional] 
**password** | **str** |  | [optional] 
**from_address** | **str** |  | [optional] 
**to_addresses** | **List[str]** |  | [optional] 
**notification_id** | **str** |  | 
**email_id** | **str** |  | 

## Example

```python
from openapi_client.models.notification_update_email_request import NotificationUpdateEmailRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationUpdateEmailRequest from a JSON string
notification_update_email_request_instance = NotificationUpdateEmailRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationUpdateEmailRequest.to_json())

# convert the object into a dict
notification_update_email_request_dict = notification_update_email_request_instance.to_dict()
# create an instance of NotificationUpdateEmailRequest from a dict
notification_update_email_request_from_dict = NotificationUpdateEmailRequest.from_dict(notification_update_email_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


