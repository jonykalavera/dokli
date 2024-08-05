# SettingsUpdateTraefikFileRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**path** | **str** |  | 
**traefik_config** | **str** |  | 

## Example

```python
from openapi_client.models.settings_update_traefik_file_request import SettingsUpdateTraefikFileRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsUpdateTraefikFileRequest from a JSON string
settings_update_traefik_file_request_instance = SettingsUpdateTraefikFileRequest.from_json(json)
# print the JSON string representation of the object
print(SettingsUpdateTraefikFileRequest.to_json())

# convert the object into a dict
settings_update_traefik_file_request_dict = settings_update_traefik_file_request_instance.to_dict()
# create an instance of SettingsUpdateTraefikFileRequest from a dict
settings_update_traefik_file_request_from_dict = SettingsUpdateTraefikFileRequest.from_dict(settings_update_traefik_file_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


