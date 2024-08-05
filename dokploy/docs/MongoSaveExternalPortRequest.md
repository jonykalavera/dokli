# MongoSaveExternalPortRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mongo_id** | **str** |  | 
**external_port** | **float** |  | 

## Example

```python
from openapi_client.models.mongo_save_external_port_request import MongoSaveExternalPortRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MongoSaveExternalPortRequest from a JSON string
mongo_save_external_port_request_instance = MongoSaveExternalPortRequest.from_json(json)
# print the JSON string representation of the object
print(MongoSaveExternalPortRequest.to_json())

# convert the object into a dict
mongo_save_external_port_request_dict = mongo_save_external_port_request_instance.to_dict()
# create an instance of MongoSaveExternalPortRequest from a dict
mongo_save_external_port_request_from_dict = MongoSaveExternalPortRequest.from_dict(mongo_save_external_port_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


