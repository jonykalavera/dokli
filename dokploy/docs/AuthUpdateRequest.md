# AuthUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**email** | **str** |  | 
**password** | **str** |  | 
**rol** | **str** |  | [optional] 
**image** | **str** |  | [optional] 
**secret** | **str** |  | [optional] 
**token** | **str** |  | [optional] 
**is2_fa_enabled** | **bool** |  | [optional] 
**created_at** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.auth_update_request import AuthUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AuthUpdateRequest from a JSON string
auth_update_request_instance = AuthUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(AuthUpdateRequest.to_json())

# convert the object into a dict
auth_update_request_dict = auth_update_request_instance.to_dict()
# create an instance of AuthUpdateRequest from a dict
auth_update_request_from_dict = AuthUpdateRequest.from_dict(auth_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


