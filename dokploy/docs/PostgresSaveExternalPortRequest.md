# PostgresSaveExternalPortRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**postgres_id** | **str** |  | 
**external_port** | **float** |  | 

## Example

```python
from openapi_client.models.postgres_save_external_port_request import PostgresSaveExternalPortRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostgresSaveExternalPortRequest from a JSON string
postgres_save_external_port_request_instance = PostgresSaveExternalPortRequest.from_json(json)
# print the JSON string representation of the object
print(PostgresSaveExternalPortRequest.to_json())

# convert the object into a dict
postgres_save_external_port_request_dict = postgres_save_external_port_request_instance.to_dict()
# create an instance of PostgresSaveExternalPortRequest from a dict
postgres_save_external_port_request_from_dict = PostgresSaveExternalPortRequest.from_dict(postgres_save_external_port_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


