# RedisSaveExternalPortRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**redis_id** | **str** |  | 
**external_port** | **float** |  | 

## Example

```python
from openapi_client.models.redis_save_external_port_request import RedisSaveExternalPortRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedisSaveExternalPortRequest from a JSON string
redis_save_external_port_request_instance = RedisSaveExternalPortRequest.from_json(json)
# print the JSON string representation of the object
print(RedisSaveExternalPortRequest.to_json())

# convert the object into a dict
redis_save_external_port_request_dict = redis_save_external_port_request_instance.to_dict()
# create an instance of RedisSaveExternalPortRequest from a dict
redis_save_external_port_request_from_dict = RedisSaveExternalPortRequest.from_dict(redis_save_external_port_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


