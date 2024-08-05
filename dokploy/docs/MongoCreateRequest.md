# MongoCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**app_name** | **str** |  | 
**docker_image** | **str** |  | [optional] [default to 'mongo:15']
**project_id** | **str** |  | 
**description** | **str** |  | [optional] 
**database_user** | **str** |  | 
**database_password** | **str** |  | 

## Example

```python
from openapi_client.models.mongo_create_request import MongoCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MongoCreateRequest from a JSON string
mongo_create_request_instance = MongoCreateRequest.from_json(json)
# print the JSON string representation of the object
print(MongoCreateRequest.to_json())

# convert the object into a dict
mongo_create_request_dict = mongo_create_request_instance.to_dict()
# create an instance of MongoCreateRequest from a dict
mongo_create_request_from_dict = MongoCreateRequest.from_dict(mongo_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


