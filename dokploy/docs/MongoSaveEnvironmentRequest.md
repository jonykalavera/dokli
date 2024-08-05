# MongoSaveEnvironmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mongo_id** | **str** |  | 
**env** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.mongo_save_environment_request import MongoSaveEnvironmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MongoSaveEnvironmentRequest from a JSON string
mongo_save_environment_request_instance = MongoSaveEnvironmentRequest.from_json(json)
# print the JSON string representation of the object
print(MongoSaveEnvironmentRequest.to_json())

# convert the object into a dict
mongo_save_environment_request_dict = mongo_save_environment_request_instance.to_dict()
# create an instance of MongoSaveEnvironmentRequest from a dict
mongo_save_environment_request_from_dict = MongoSaveEnvironmentRequest.from_dict(mongo_save_environment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


