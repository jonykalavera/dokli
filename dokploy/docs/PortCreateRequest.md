# PortCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**published_port** | **float** |  | 
**target_port** | **float** |  | 
**protocol** | **str** |  | [optional] [default to 'tcp']
**application_id** | **str** |  | 

## Example

```python
from openapi_client.models.port_create_request import PortCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PortCreateRequest from a JSON string
port_create_request_instance = PortCreateRequest.from_json(json)
# print the JSON string representation of the object
print(PortCreateRequest.to_json())

# convert the object into a dict
port_create_request_dict = port_create_request_instance.to_dict()
# create an instance of PortCreateRequest from a dict
port_create_request_from_dict = PortCreateRequest.from_dict(port_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


