# ComposeUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**compose_id** | **str** |  | 
**name** | **str** |  | [optional] 
**app_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**env** | **str** |  | [optional] 
**compose_file** | **str** |  | [optional] 
**refresh_token** | **str** |  | [optional] 
**source_type** | **str** |  | [optional] 
**compose_type** | **str** |  | [optional] 
**repository** | **str** |  | [optional] 
**owner** | **str** |  | [optional] 
**branch** | **str** |  | [optional] 
**auto_deploy** | **bool** |  | [optional] 
**custom_git_url** | **str** |  | [optional] 
**custom_git_branch** | **str** |  | [optional] 
**custom_git_ssh_key_id** | **str** |  | [optional] 
**command** | **str** |  | [optional] 
**compose_path** | **str** |  | [optional] 
**compose_status** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 
**created_at** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.compose_update_request import ComposeUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ComposeUpdateRequest from a JSON string
compose_update_request_instance = ComposeUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ComposeUpdateRequest.to_json())

# convert the object into a dict
compose_update_request_dict = compose_update_request_instance.to_dict()
# create an instance of ComposeUpdateRequest from a dict
compose_update_request_from_dict = ComposeUpdateRequest.from_dict(compose_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


