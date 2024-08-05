# MysqlCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**app_name** | **str** |  | 
**docker_image** | **str** |  | [optional] [default to 'mysql:8']
**project_id** | **str** |  | 
**description** | **str** |  | [optional] 
**database_name** | **str** |  | 
**database_user** | **str** |  | 
**database_password** | **str** |  | 
**database_root_password** | **str** |  | 

## Example

```python
from openapi_client.models.mysql_create_request import MysqlCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MysqlCreateRequest from a JSON string
mysql_create_request_instance = MysqlCreateRequest.from_json(json)
# print the JSON string representation of the object
print(MysqlCreateRequest.to_json())

# convert the object into a dict
mysql_create_request_dict = mysql_create_request_instance.to_dict()
# create an instance of MysqlCreateRequest from a dict
mysql_create_request_from_dict = MysqlCreateRequest.from_dict(mysql_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


