# RegistryCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registry_name** | **str** |  | 
**username** | **str** |  | 
**password** | **str** |  | 
**registry_url** | **str** |  | 
**registry_type** | **str** |  | 
**image_prefix** | **str** |  | 

## Example

```python
from openapi_client.models.registry_create_request import RegistryCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RegistryCreateRequest from a JSON string
registry_create_request_instance = RegistryCreateRequest.from_json(json)
# print the JSON string representation of the object
print(RegistryCreateRequest.to_json())

# convert the object into a dict
registry_create_request_dict = registry_create_request_instance.to_dict()
# create an instance of RegistryCreateRequest from a dict
registry_create_request_from_dict = RegistryCreateRequest.from_dict(registry_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


