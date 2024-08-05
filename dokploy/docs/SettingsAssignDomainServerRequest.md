# SettingsAssignDomainServerRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**lets_encrypt_email** | **str** |  | 
**host** | **str** |  | 
**certificate_type** | **str** |  | [optional] [default to 'none']

## Example

```python
from openapi_client.models.settings_assign_domain_server_request import SettingsAssignDomainServerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsAssignDomainServerRequest from a JSON string
settings_assign_domain_server_request_instance = SettingsAssignDomainServerRequest.from_json(json)
# print the JSON string representation of the object
print(SettingsAssignDomainServerRequest.to_json())

# convert the object into a dict
settings_assign_domain_server_request_dict = settings_assign_domain_server_request_instance.to_dict()
# create an instance of SettingsAssignDomainServerRequest from a dict
settings_assign_domain_server_request_from_dict = SettingsAssignDomainServerRequest.from_dict(settings_assign_domain_server_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


