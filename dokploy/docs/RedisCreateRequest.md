# RedisCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**app_name** | **str** |  | 
**database_password** | **str** |  | 
**docker_image** | **str** |  | [optional] [default to 'redis:8']
**project_id** | **str** |  | 
**description** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.redis_create_request import RedisCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedisCreateRequest from a JSON string
redis_create_request_instance = RedisCreateRequest.from_json(json)
# print the JSON string representation of the object
print(RedisCreateRequest.to_json())

# convert the object into a dict
redis_create_request_dict = redis_create_request_instance.to_dict()
# create an instance of RedisCreateRequest from a dict
redis_create_request_from_dict = RedisCreateRequest.from_dict(redis_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


