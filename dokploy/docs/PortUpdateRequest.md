# PortUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**port_id** | **str** |  | 
**published_port** | **float** |  | 
**target_port** | **float** |  | 
**protocol** | **str** |  | [optional] [default to 'tcp']

## Example

```python
from openapi_client.models.port_update_request import PortUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PortUpdateRequest from a JSON string
port_update_request_instance = PortUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(PortUpdateRequest.to_json())

# convert the object into a dict
port_update_request_dict = port_update_request_instance.to_dict()
# create an instance of PortUpdateRequest from a dict
port_update_request_from_dict = PortUpdateRequest.from_dict(port_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


