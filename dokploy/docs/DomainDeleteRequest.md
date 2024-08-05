# DomainDeleteRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**domain_id** | **str** |  | 

## Example

```python
from openapi_client.models.domain_delete_request import DomainDeleteRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DomainDeleteRequest from a JSON string
domain_delete_request_instance = DomainDeleteRequest.from_json(json)
# print the JSON string representation of the object
print(DomainDeleteRequest.to_json())

# convert the object into a dict
domain_delete_request_dict = domain_delete_request_instance.to_dict()
# create an instance of DomainDeleteRequest from a dict
domain_delete_request_from_dict = DomainDeleteRequest.from_dict(domain_delete_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


