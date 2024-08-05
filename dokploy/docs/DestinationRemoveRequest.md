# DestinationRemoveRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**destination_id** | **str** |  | 

## Example

```python
from openapi_client.models.destination_remove_request import DestinationRemoveRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DestinationRemoveRequest from a JSON string
destination_remove_request_instance = DestinationRemoveRequest.from_json(json)
# print the JSON string representation of the object
print(DestinationRemoveRequest.to_json())

# convert the object into a dict
destination_remove_request_dict = destination_remove_request_instance.to_dict()
# create an instance of DestinationRemoveRequest from a dict
destination_remove_request_from_dict = DestinationRemoveRequest.from_dict(destination_remove_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


