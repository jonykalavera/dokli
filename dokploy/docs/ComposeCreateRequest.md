# ComposeCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | [optional] 
**project_id** | **str** |  | 
**compose_type** | **str** |  | [optional] 
**app_name** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.compose_create_request import ComposeCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ComposeCreateRequest from a JSON string
compose_create_request_instance = ComposeCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ComposeCreateRequest.to_json())

# convert the object into a dict
compose_create_request_dict = compose_create_request_instance.to_dict()
# create an instance of ComposeCreateRequest from a dict
compose_create_request_from_dict = ComposeCreateRequest.from_dict(compose_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


