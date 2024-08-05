# ApplicationSaveDockerProviderRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**docker_image** | **str** |  | [optional] 
**application_id** | **str** |  | 
**username** | **str** |  | [optional] 
**password** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.application_save_docker_provider_request import ApplicationSaveDockerProviderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationSaveDockerProviderRequest from a JSON string
application_save_docker_provider_request_instance = ApplicationSaveDockerProviderRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationSaveDockerProviderRequest.to_json())

# convert the object into a dict
application_save_docker_provider_request_dict = application_save_docker_provider_request_instance.to_dict()
# create an instance of ApplicationSaveDockerProviderRequest from a dict
application_save_docker_provider_request_from_dict = ApplicationSaveDockerProviderRequest.from_dict(application_save_docker_provider_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


