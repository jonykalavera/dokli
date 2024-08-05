# MongoChangeStatusRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mongo_id** | **str** |  | 
**application_status** | **str** |  | 

## Example

```python
from openapi_client.models.mongo_change_status_request import MongoChangeStatusRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MongoChangeStatusRequest from a JSON string
mongo_change_status_request_instance = MongoChangeStatusRequest.from_json(json)
# print the JSON string representation of the object
print(MongoChangeStatusRequest.to_json())

# convert the object into a dict
mongo_change_status_request_dict = mongo_change_status_request_instance.to_dict()
# create an instance of MongoChangeStatusRequest from a dict
mongo_change_status_request_from_dict = MongoChangeStatusRequest.from_dict(mongo_change_status_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


