# ApplicationUpdateTraefikConfigRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_id** | **str** |  | 
**traefik_config** | **str** |  | 

## Example

```python
from openapi_client.models.application_update_traefik_config_request import ApplicationUpdateTraefikConfigRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateTraefikConfigRequest from a JSON string
application_update_traefik_config_request_instance = ApplicationUpdateTraefikConfigRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateTraefikConfigRequest.to_json())

# convert the object into a dict
application_update_traefik_config_request_dict = application_update_traefik_config_request_instance.to_dict()
# create an instance of ApplicationUpdateTraefikConfigRequest from a dict
application_update_traefik_config_request_from_dict = ApplicationUpdateTraefikConfigRequest.from_dict(application_update_traefik_config_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


