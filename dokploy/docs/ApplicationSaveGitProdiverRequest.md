# ApplicationSaveGitProdiverRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_git_branch** | **str** |  | [optional] 
**application_id** | **str** |  | 
**custom_git_build_path** | **str** |  | [optional] 
**custom_git_url** | **str** |  | [optional] 
**custom_git_ssh_key_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.application_save_git_prodiver_request import ApplicationSaveGitProdiverRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationSaveGitProdiverRequest from a JSON string
application_save_git_prodiver_request_instance = ApplicationSaveGitProdiverRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationSaveGitProdiverRequest.to_json())

# convert the object into a dict
application_save_git_prodiver_request_dict = application_save_git_prodiver_request_instance.to_dict()
# create an instance of ApplicationSaveGitProdiverRequest from a dict
application_save_git_prodiver_request_from_dict = ApplicationSaveGitProdiverRequest.from_dict(application_save_git_prodiver_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


