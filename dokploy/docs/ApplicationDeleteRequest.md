# ApplicationDeleteRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_id** | **str** |  | 

## Example

```python
from openapi_client.models.application_delete_request import ApplicationDeleteRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationDeleteRequest from a JSON string
application_delete_request_instance = ApplicationDeleteRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationDeleteRequest.to_json())

# convert the object into a dict
application_delete_request_dict = application_delete_request_instance.to_dict()
# create an instance of ApplicationDeleteRequest from a dict
application_delete_request_from_dict = ApplicationDeleteRequest.from_dict(application_delete_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


