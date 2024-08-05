# SettingsSaveSSHPrivateKeyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ssh_private_key** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.settings_save_ssh_private_key_request import SettingsSaveSSHPrivateKeyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsSaveSSHPrivateKeyRequest from a JSON string
settings_save_ssh_private_key_request_instance = SettingsSaveSSHPrivateKeyRequest.from_json(json)
# print the JSON string representation of the object
print(SettingsSaveSSHPrivateKeyRequest.to_json())

# convert the object into a dict
settings_save_ssh_private_key_request_dict = settings_save_ssh_private_key_request_instance.to_dict()
# create an instance of SettingsSaveSSHPrivateKeyRequest from a dict
settings_save_ssh_private_key_request_from_dict = SettingsSaveSSHPrivateKeyRequest.from_dict(settings_save_ssh_private_key_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


