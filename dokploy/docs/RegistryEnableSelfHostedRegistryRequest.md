# RegistryEnableSelfHostedRegistryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registry_url** | **str** |  | 
**username** | **str** |  | 
**password** | **str** |  | 

## Example

```python
from openapi_client.models.registry_enable_self_hosted_registry_request import RegistryEnableSelfHostedRegistryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RegistryEnableSelfHostedRegistryRequest from a JSON string
registry_enable_self_hosted_registry_request_instance = RegistryEnableSelfHostedRegistryRequest.from_json(json)
# print the JSON string representation of the object
print(RegistryEnableSelfHostedRegistryRequest.to_json())

# convert the object into a dict
registry_enable_self_hosted_registry_request_dict = registry_enable_self_hosted_registry_request_instance.to_dict()
# create an instance of RegistryEnableSelfHostedRegistryRequest from a dict
registry_enable_self_hosted_registry_request_from_dict = RegistryEnableSelfHostedRegistryRequest.from_dict(registry_enable_self_hosted_registry_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


