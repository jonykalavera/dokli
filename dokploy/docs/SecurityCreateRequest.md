# SecurityCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_id** | **str** |  | 
**username** | **str** |  | 
**password** | **str** |  | 

## Example

```python
from openapi_client.models.security_create_request import SecurityCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SecurityCreateRequest from a JSON string
security_create_request_instance = SecurityCreateRequest.from_json(json)
# print the JSON string representation of the object
print(SecurityCreateRequest.to_json())

# convert the object into a dict
security_create_request_dict = security_create_request_instance.to_dict()
# create an instance of SecurityCreateRequest from a dict
security_create_request_from_dict = SecurityCreateRequest.from_dict(security_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


