# AdminRemoveUserRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auth_id** | **str** |  | 

## Example

```python
from openapi_client.models.admin_remove_user_request import AdminRemoveUserRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AdminRemoveUserRequest from a JSON string
admin_remove_user_request_instance = AdminRemoveUserRequest.from_json(json)
# print the JSON string representation of the object
print(AdminRemoveUserRequest.to_json())

# convert the object into a dict
admin_remove_user_request_dict = admin_remove_user_request_instance.to_dict()
# create an instance of AdminRemoveUserRequest from a dict
admin_remove_user_request_from_dict = AdminRemoveUserRequest.from_dict(admin_remove_user_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


