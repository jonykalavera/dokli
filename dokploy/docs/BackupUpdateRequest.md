# BackupUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**schedule** | **str** |  | 
**enabled** | **bool** |  | [optional] 
**prefix** | **str** |  | 
**backup_id** | **str** |  | 
**destination_id** | **str** |  | 
**database** | **str** |  | 

## Example

```python
from openapi_client.models.backup_update_request import BackupUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BackupUpdateRequest from a JSON string
backup_update_request_instance = BackupUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(BackupUpdateRequest.to_json())

# convert the object into a dict
backup_update_request_dict = backup_update_request_instance.to_dict()
# create an instance of BackupUpdateRequest from a dict
backup_update_request_from_dict = BackupUpdateRequest.from_dict(backup_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


