# SettingsToggleDashboardRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enable_dashboard** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.settings_toggle_dashboard_request import SettingsToggleDashboardRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsToggleDashboardRequest from a JSON string
settings_toggle_dashboard_request_instance = SettingsToggleDashboardRequest.from_json(json)
# print the JSON string representation of the object
print(SettingsToggleDashboardRequest.to_json())

# convert the object into a dict
settings_toggle_dashboard_request_dict = settings_toggle_dashboard_request_instance.to_dict()
# create an instance of SettingsToggleDashboardRequest from a dict
settings_toggle_dashboard_request_from_dict = SettingsToggleDashboardRequest.from_dict(settings_toggle_dashboard_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


