# SshKeyGenerateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.ssh_key_generate_request import SshKeyGenerateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SshKeyGenerateRequest from a JSON string
ssh_key_generate_request_instance = SshKeyGenerateRequest.from_json(json)
# print the JSON string representation of the object
print(SshKeyGenerateRequest.to_json())

# convert the object into a dict
ssh_key_generate_request_dict = ssh_key_generate_request_instance.to_dict()
# create an instance of SshKeyGenerateRequest from a dict
ssh_key_generate_request_from_dict = SshKeyGenerateRequest.from_dict(ssh_key_generate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


