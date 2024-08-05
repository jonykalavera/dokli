# SshKeyRemoveRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ssh_key_id** | **str** |  | 

## Example

```python
from openapi_client.models.ssh_key_remove_request import SshKeyRemoveRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SshKeyRemoveRequest from a JSON string
ssh_key_remove_request_instance = SshKeyRemoveRequest.from_json(json)
# print the JSON string representation of the object
print(SshKeyRemoveRequest.to_json())

# convert the object into a dict
ssh_key_remove_request_dict = ssh_key_remove_request_instance.to_dict()
# create an instance of SshKeyRemoveRequest from a dict
ssh_key_remove_request_from_dict = SshKeyRemoveRequest.from_dict(ssh_key_remove_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


