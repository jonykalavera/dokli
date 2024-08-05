# RedisChangeStatusRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**redis_id** | **str** |  | 
**application_status** | **str** |  | 

## Example

```python
from openapi_client.models.redis_change_status_request import RedisChangeStatusRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedisChangeStatusRequest from a JSON string
redis_change_status_request_instance = RedisChangeStatusRequest.from_json(json)
# print the JSON string representation of the object
print(RedisChangeStatusRequest.to_json())

# convert the object into a dict
redis_change_status_request_dict = redis_change_status_request_instance.to_dict()
# create an instance of RedisChangeStatusRequest from a dict
redis_change_status_request_from_dict = RedisChangeStatusRequest.from_dict(redis_change_status_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


