# ApplicationSaveEnvironmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_id** | **str** |  | 
**env** | **str** |  | [optional] 
**build_args** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.application_save_environment_request import ApplicationSaveEnvironmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationSaveEnvironmentRequest from a JSON string
application_save_environment_request_instance = ApplicationSaveEnvironmentRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationSaveEnvironmentRequest.to_json())

# convert the object into a dict
application_save_environment_request_dict = application_save_environment_request_instance.to_dict()
# create an instance of ApplicationSaveEnvironmentRequest from a dict
application_save_environment_request_from_dict = ApplicationSaveEnvironmentRequest.from_dict(application_save_environment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


