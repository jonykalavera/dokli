# DomainCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**host** | **str** |  | 
**path** | **str** |  | [optional] 
**port** | **float** |  | [optional] 
**https** | **bool** |  | [optional] 
**application_id** | **str** |  | 
**certificate_type** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.domain_create_request import DomainCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DomainCreateRequest from a JSON string
domain_create_request_instance = DomainCreateRequest.from_json(json)
# print the JSON string representation of the object
print(DomainCreateRequest.to_json())

# convert the object into a dict
domain_create_request_dict = domain_create_request_instance.to_dict()
# create an instance of DomainCreateRequest from a dict
domain_create_request_from_dict = DomainCreateRequest.from_dict(domain_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


