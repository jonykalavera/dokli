# BackupCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**schedule** | **str** |  | 
**enabled** | **bool** |  | [optional] 
**prefix** | **str** |  | 
**destination_id** | **str** |  | 
**database** | **str** |  | 
**mariadb_id** | **str** |  | [optional] 
**mysql_id** | **str** |  | [optional] 
**postgres_id** | **str** |  | [optional] 
**mongo_id** | **str** |  | [optional] 
**database_type** | **str** |  | 

## Example

```python
from openapi_client.models.backup_create_request import BackupCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BackupCreateRequest from a JSON string
backup_create_request_instance = BackupCreateRequest.from_json(json)
# print the JSON string representation of the object
print(BackupCreateRequest.to_json())

# convert the object into a dict
backup_create_request_dict = backup_create_request_instance.to_dict()
# create an instance of BackupCreateRequest from a dict
backup_create_request_from_dict = BackupCreateRequest.from_dict(backup_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


