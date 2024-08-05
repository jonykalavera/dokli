# RedisReloadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**redis_id** | **str** |  | 
**app_name** | **str** |  | 

## Example

```python
from openapi_client.models.redis_reload_request import RedisReloadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedisReloadRequest from a JSON string
redis_reload_request_instance = RedisReloadRequest.from_json(json)
# print the JSON string representation of the object
print(RedisReloadRequest.to_json())

# convert the object into a dict
redis_reload_request_dict = redis_reload_request_instance.to_dict()
# create an instance of RedisReloadRequest from a dict
redis_reload_request_from_dict = RedisReloadRequest.from_dict(redis_reload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


