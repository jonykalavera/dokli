# AuthCreateUserRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**password** | **str** |  | 
**id** | **str** |  | 
**token** | **str** |  | 

## Example

```python
from openapi_client.models.auth_create_user_request import AuthCreateUserRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AuthCreateUserRequest from a JSON string
auth_create_user_request_instance = AuthCreateUserRequest.from_json(json)
# print the JSON string representation of the object
print(AuthCreateUserRequest.to_json())

# convert the object into a dict
auth_create_user_request_dict = auth_create_user_request_instance.to_dict()
# create an instance of AuthCreateUserRequest from a dict
auth_create_user_request_from_dict = AuthCreateUserRequest.from_dict(auth_create_user_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


