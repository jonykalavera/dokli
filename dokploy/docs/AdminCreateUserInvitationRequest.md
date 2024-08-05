# AdminCreateUserInvitationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | 

## Example

```python
from openapi_client.models.admin_create_user_invitation_request import AdminCreateUserInvitationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AdminCreateUserInvitationRequest from a JSON string
admin_create_user_invitation_request_instance = AdminCreateUserInvitationRequest.from_json(json)
# print the JSON string representation of the object
print(AdminCreateUserInvitationRequest.to_json())

# convert the object into a dict
admin_create_user_invitation_request_dict = admin_create_user_invitation_request_instance.to_dict()
# create an instance of AdminCreateUserInvitationRequest from a dict
admin_create_user_invitation_request_from_dict = AdminCreateUserInvitationRequest.from_dict(admin_create_user_invitation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


