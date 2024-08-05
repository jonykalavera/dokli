# DestinationUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**access_key** | **str** |  | 
**bucket** | **str** |  | 
**region** | **str** |  | 
**endpoint** | **str** |  | 
**secret_access_key** | **str** |  | 
**destination_id** | **str** |  | 

## Example

```python
from openapi_client.models.destination_update_request import DestinationUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DestinationUpdateRequest from a JSON string
destination_update_request_instance = DestinationUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(DestinationUpdateRequest.to_json())

# convert the object into a dict
destination_update_request_dict = destination_update_request_instance.to_dict()
# create an instance of DestinationUpdateRequest from a dict
destination_update_request_from_dict = DestinationUpdateRequest.from_dict(destination_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


