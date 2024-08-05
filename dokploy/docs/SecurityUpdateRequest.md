# SecurityUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**security_id** | **str** |  | 
**username** | **str** |  | 
**password** | **str** |  | 

## Example

```python
from openapi_client.models.security_update_request import SecurityUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SecurityUpdateRequest from a JSON string
security_update_request_instance = SecurityUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(SecurityUpdateRequest.to_json())

# convert the object into a dict
security_update_request_dict = security_update_request_instance.to_dict()
# create an instance of SecurityUpdateRequest from a dict
security_update_request_from_dict = SecurityUpdateRequest.from_dict(security_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


