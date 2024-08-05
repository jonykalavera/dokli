# RedisStartRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**redis_id** | **str** |  | 

## Example

```python
from openapi_client.models.redis_start_request import RedisStartRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedisStartRequest from a JSON string
redis_start_request_instance = RedisStartRequest.from_json(json)
# print the JSON string representation of the object
print(RedisStartRequest.to_json())

# convert the object into a dict
redis_start_request_dict = redis_start_request_instance.to_dict()
# create an instance of RedisStartRequest from a dict
redis_start_request_from_dict = RedisStartRequest.from_dict(redis_start_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


