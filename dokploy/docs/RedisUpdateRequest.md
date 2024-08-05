# RedisUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**redis_id** | **str** |  | 
**name** | **str** |  | [optional] 
**app_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**database_password** | **str** |  | [optional] 
**docker_image** | **str** |  | [optional] [default to 'redis:8']
**command** | **str** |  | [optional] 
**env** | **str** |  | [optional] 
**memory_reservation** | **float** |  | [optional] 
**memory_limit** | **float** |  | [optional] 
**cpu_reservation** | **float** |  | [optional] 
**cpu_limit** | **float** |  | [optional] 
**external_port** | **float** |  | [optional] 
**created_at** | **str** |  | [optional] 
**application_status** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.redis_update_request import RedisUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedisUpdateRequest from a JSON string
redis_update_request_instance = RedisUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(RedisUpdateRequest.to_json())

# convert the object into a dict
redis_update_request_dict = redis_update_request_instance.to_dict()
# create an instance of RedisUpdateRequest from a dict
redis_update_request_from_dict = RedisUpdateRequest.from_dict(redis_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


