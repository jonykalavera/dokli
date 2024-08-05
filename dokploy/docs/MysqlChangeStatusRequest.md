# MysqlChangeStatusRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mysql_id** | **str** |  | 
**application_status** | **str** |  | 

## Example

```python
from openapi_client.models.mysql_change_status_request import MysqlChangeStatusRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MysqlChangeStatusRequest from a JSON string
mysql_change_status_request_instance = MysqlChangeStatusRequest.from_json(json)
# print the JSON string representation of the object
print(MysqlChangeStatusRequest.to_json())

# convert the object into a dict
mysql_change_status_request_dict = mysql_change_status_request_instance.to_dict()
# create an instance of MysqlChangeStatusRequest from a dict
mysql_change_status_request_from_dict = MysqlChangeStatusRequest.from_dict(mysql_change_status_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


