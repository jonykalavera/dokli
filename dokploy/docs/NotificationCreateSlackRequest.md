# NotificationCreateSlackRequest


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
**channel** | **str** |  | 

## Example

```python
from openapi_client.models.notification_create_slack_request import NotificationCreateSlackRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationCreateSlackRequest from a JSON string
notification_create_slack_request_instance = NotificationCreateSlackRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationCreateSlackRequest.to_json())

# convert the object into a dict
notification_create_slack_request_dict = notification_create_slack_request_instance.to_dict()
# create an instance of NotificationCreateSlackRequest from a dict
notification_create_slack_request_from_dict = NotificationCreateSlackRequest.from_dict(notification_create_slack_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


