# BackupRemoveRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backup_id** | **str** |  | 

## Example

```python
from openapi_client.models.backup_remove_request import BackupRemoveRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BackupRemoveRequest from a JSON string
backup_remove_request_instance = BackupRemoveRequest.from_json(json)
# print the JSON string representation of the object
print(BackupRemoveRequest.to_json())

# convert the object into a dict
backup_remove_request_dict = backup_remove_request_instance.to_dict()
# create an instance of BackupRemoveRequest from a dict
backup_remove_request_from_dict = BackupRemoveRequest.from_dict(backup_remove_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


