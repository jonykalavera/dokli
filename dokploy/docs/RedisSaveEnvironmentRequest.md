# RedisSaveEnvironmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**redis_id** | **str** |  | 
**env** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.redis_save_environment_request import RedisSaveEnvironmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedisSaveEnvironmentRequest from a JSON string
redis_save_environment_request_instance = RedisSaveEnvironmentRequest.from_json(json)
# print the JSON string representation of the object
print(RedisSaveEnvironmentRequest.to_json())

# convert the object into a dict
redis_save_environment_request_dict = redis_save_environment_request_instance.to_dict()
# create an instance of RedisSaveEnvironmentRequest from a dict
redis_save_environment_request_from_dict = RedisSaveEnvironmentRequest.from_dict(redis_save_environment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


