# MysqlReloadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mysql_id** | **str** |  | 
**app_name** | **str** |  | 

## Example

```python
from openapi_client.models.mysql_reload_request import MysqlReloadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MysqlReloadRequest from a JSON string
mysql_reload_request_instance = MysqlReloadRequest.from_json(json)
# print the JSON string representation of the object
print(MysqlReloadRequest.to_json())

# convert the object into a dict
mysql_reload_request_dict = mysql_reload_request_instance.to_dict()
# create an instance of MysqlReloadRequest from a dict
mysql_reload_request_from_dict = MysqlReloadRequest.from_dict(mysql_reload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


