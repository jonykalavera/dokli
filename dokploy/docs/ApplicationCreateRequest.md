# ApplicationCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**app_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**project_id** | **str** |  | 

## Example

```python
from openapi_client.models.application_create_request import ApplicationCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationCreateRequest from a JSON string
application_create_request_instance = ApplicationCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationCreateRequest.to_json())

# convert the object into a dict
application_create_request_dict = application_create_request_instance.to_dict()
# create an instance of ApplicationCreateRequest from a dict
application_create_request_from_dict = ApplicationCreateRequest.from_dict(application_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


