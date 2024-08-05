# ApplicationSaveGithubProviderRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_id** | **str** |  | 
**repository** | **str** |  | [optional] 
**branch** | **str** |  | [optional] 
**owner** | **str** |  | 
**build_path** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.application_save_github_provider_request import ApplicationSaveGithubProviderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationSaveGithubProviderRequest from a JSON string
application_save_github_provider_request_instance = ApplicationSaveGithubProviderRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationSaveGithubProviderRequest.to_json())

# convert the object into a dict
application_save_github_provider_request_dict = application_save_github_provider_request_instance.to_dict()
# create an instance of ApplicationSaveGithubProviderRequest from a dict
application_save_github_provider_request_from_dict = ApplicationSaveGithubProviderRequest.from_dict(application_save_github_provider_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


