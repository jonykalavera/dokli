# ApplicationReloadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_name** | **str** |  | 
**application_id** | **str** |  | 

## Example

```python
from openapi_client.models.application_reload_request import ApplicationReloadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationReloadRequest from a JSON string
application_reload_request_instance = ApplicationReloadRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationReloadRequest.to_json())

# convert the object into a dict
application_reload_request_dict = application_reload_request_instance.to_dict()
# create an instance of ApplicationReloadRequest from a dict
application_reload_request_from_dict = ApplicationReloadRequest.from_dict(application_reload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


