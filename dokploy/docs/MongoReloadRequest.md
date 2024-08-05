# MongoReloadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mongo_id** | **str** |  | 
**app_name** | **str** |  | 

## Example

```python
from openapi_client.models.mongo_reload_request import MongoReloadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MongoReloadRequest from a JSON string
mongo_reload_request_instance = MongoReloadRequest.from_json(json)
# print the JSON string representation of the object
print(MongoReloadRequest.to_json())

# convert the object into a dict
mongo_reload_request_dict = mongo_reload_request_instance.to_dict()
# create an instance of MongoReloadRequest from a dict
mongo_reload_request_from_dict = MongoReloadRequest.from_dict(mongo_reload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


