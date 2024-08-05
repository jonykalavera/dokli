# MysqlSaveEnvironmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mysql_id** | **str** |  | 
**env** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.mysql_save_environment_request import MysqlSaveEnvironmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MysqlSaveEnvironmentRequest from a JSON string
mysql_save_environment_request_instance = MysqlSaveEnvironmentRequest.from_json(json)
# print the JSON string representation of the object
print(MysqlSaveEnvironmentRequest.to_json())

# convert the object into a dict
mysql_save_environment_request_dict = mysql_save_environment_request_instance.to_dict()
# create an instance of MysqlSaveEnvironmentRequest from a dict
mysql_save_environment_request_from_dict = MysqlSaveEnvironmentRequest.from_dict(mysql_save_environment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


