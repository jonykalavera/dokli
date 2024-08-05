# SshKeyUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**last_used_at** | **str** |  | [optional] 
**ssh_key_id** | **str** |  | 

## Example

```python
from openapi_client.models.ssh_key_update_request import SshKeyUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SshKeyUpdateRequest from a JSON string
ssh_key_update_request_instance = SshKeyUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(SshKeyUpdateRequest.to_json())

# convert the object into a dict
ssh_key_update_request_dict = ssh_key_update_request_instance.to_dict()
# create an instance of SshKeyUpdateRequest from a dict
ssh_key_update_request_from_dict = SshKeyUpdateRequest.from_dict(ssh_key_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


