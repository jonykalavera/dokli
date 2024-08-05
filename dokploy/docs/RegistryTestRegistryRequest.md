# RegistryTestRegistryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registry_name** | **str** |  | 
**username** | **str** |  | 
**password** | **str** |  | 
**registry_url** | **str** |  | 
**registry_type** | **str** |  | 
**image_prefix** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.registry_test_registry_request import RegistryTestRegistryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RegistryTestRegistryRequest from a JSON string
registry_test_registry_request_instance = RegistryTestRegistryRequest.from_json(json)
# print the JSON string representation of the object
print(RegistryTestRegistryRequest.to_json())

# convert the object into a dict
registry_test_registry_request_dict = registry_test_registry_request_instance.to_dict()
# create an instance of RegistryTestRegistryRequest from a dict
registry_test_registry_request_from_dict = RegistryTestRegistryRequest.from_dict(registry_test_registry_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


