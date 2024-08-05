# AuthCreateAdminRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | 
**password** | **str** |  | 

## Example

```python
from openapi_client.models.auth_create_admin_request import AuthCreateAdminRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AuthCreateAdminRequest from a JSON string
auth_create_admin_request_instance = AuthCreateAdminRequest.from_json(json)
# print the JSON string representation of the object
print(AuthCreateAdminRequest.to_json())

# convert the object into a dict
auth_create_admin_request_dict = auth_create_admin_request_instance.to_dict()
# create an instance of AuthCreateAdminRequest from a dict
auth_create_admin_request_from_dict = AuthCreateAdminRequest.from_dict(auth_create_admin_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


