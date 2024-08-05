# SettingsUpdateDockerCleanupRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enable_docker_cleanup** | **bool** |  | 

## Example

```python
from openapi_client.models.settings_update_docker_cleanup_request import SettingsUpdateDockerCleanupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsUpdateDockerCleanupRequest from a JSON string
settings_update_docker_cleanup_request_instance = SettingsUpdateDockerCleanupRequest.from_json(json)
# print the JSON string representation of the object
print(SettingsUpdateDockerCleanupRequest.to_json())

# convert the object into a dict
settings_update_docker_cleanup_request_dict = settings_update_docker_cleanup_request_instance.to_dict()
# create an instance of SettingsUpdateDockerCleanupRequest from a dict
settings_update_docker_cleanup_request_from_dict = SettingsUpdateDockerCleanupRequest.from_dict(settings_update_docker_cleanup_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


