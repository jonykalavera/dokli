# DestinationCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**access_key** | **str** |  | 
**bucket** | **str** |  | 
**region** | **str** |  | 
**endpoint** | **str** |  | 
**secret_access_key** | **str** |  | 

## Example

```python
from openapi_client.models.destination_create_request import DestinationCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DestinationCreateRequest from a JSON string
destination_create_request_instance = DestinationCreateRequest.from_json(json)
# print the JSON string representation of the object
print(DestinationCreateRequest.to_json())

# convert the object into a dict
destination_create_request_dict = destination_create_request_instance.to_dict()
# create an instance of DestinationCreateRequest from a dict
destination_create_request_from_dict = DestinationCreateRequest.from_dict(destination_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


