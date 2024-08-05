# AdminAssignPermissionsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** |  | 
**can_create_projects** | **bool** |  | 
**can_create_services** | **bool** |  | 
**can_delete_projects** | **bool** |  | 
**can_delete_services** | **bool** |  | 
**accesed_projects** | **List[str]** |  | 
**accesed_services** | **List[str]** |  | 
**can_access_to_traefik_files** | **bool** |  | 
**can_access_to_docker** | **bool** |  | 
**can_access_to_api** | **bool** |  | 

## Example

```python
from openapi_client.models.admin_assign_permissions_request import AdminAssignPermissionsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AdminAssignPermissionsRequest from a JSON string
admin_assign_permissions_request_instance = AdminAssignPermissionsRequest.from_json(json)
# print the JSON string representation of the object
print(AdminAssignPermissionsRequest.to_json())

# convert the object into a dict
admin_assign_permissions_request_dict = admin_assign_permissions_request_instance.to_dict()
# create an instance of AdminAssignPermissionsRequest from a dict
admin_assign_permissions_request_from_dict = AdminAssignPermissionsRequest.from_dict(admin_assign_permissions_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


