# AdminOneDefaultResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** |  | 
**code** | **str** |  | 
**issues** | [**List[AdminOneDefaultResponseIssuesInner]**](AdminOneDefaultResponseIssuesInner.md) |  | [optional] 

## Example

```python
from openapi_client.models.admin_one_default_response import AdminOneDefaultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AdminOneDefaultResponse from a JSON string
admin_one_default_response_instance = AdminOneDefaultResponse.from_json(json)
# print the JSON string representation of the object
print(AdminOneDefaultResponse.to_json())

# convert the object into a dict
admin_one_default_response_dict = admin_one_default_response_instance.to_dict()
# create an instance of AdminOneDefaultResponse from a dict
admin_one_default_response_from_dict = AdminOneDefaultResponse.from_dict(admin_one_default_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


