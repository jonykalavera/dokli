# MysqlSaveExternalPortRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mysql_id** | **str** |  | 
**external_port** | **float** |  | 

## Example

```python
from openapi_client.models.mysql_save_external_port_request import MysqlSaveExternalPortRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MysqlSaveExternalPortRequest from a JSON string
mysql_save_external_port_request_instance = MysqlSaveExternalPortRequest.from_json(json)
# print the JSON string representation of the object
print(MysqlSaveExternalPortRequest.to_json())

# convert the object into a dict
mysql_save_external_port_request_dict = mysql_save_external_port_request_instance.to_dict()
# create an instance of MysqlSaveExternalPortRequest from a dict
mysql_save_external_port_request_from_dict = MysqlSaveExternalPortRequest.from_dict(mysql_save_external_port_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


