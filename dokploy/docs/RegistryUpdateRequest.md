# RegistryUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registry_id** | **str** |  | 
**registry_name** | **str** |  | [optional] 
**image_prefix** | **str** |  | [optional] 
**username** | **str** |  | [optional] 
**password** | **str** |  | [optional] 
**registry_url** | **str** |  | [optional] 
**created_at** | **str** |  | [optional] 
**registry_type** | **str** |  | [optional] 
**admin_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.registry_update_request import RegistryUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RegistryUpdateRequest from a JSON string
registry_update_request_instance = RegistryUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(RegistryUpdateRequest.to_json())

# convert the object into a dict
registry_update_request_dict = registry_update_request_instance.to_dict()
# create an instance of RegistryUpdateRequest from a dict
registry_update_request_from_dict = RegistryUpdateRequest.from_dict(registry_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


