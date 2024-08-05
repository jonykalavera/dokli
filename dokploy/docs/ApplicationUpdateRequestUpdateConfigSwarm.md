# ApplicationUpdateRequestUpdateConfigSwarm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parallelism** | **float** |  | 
**delay** | **float** |  | [optional] 
**failure_action** | **str** |  | [optional] 
**monitor** | **float** |  | [optional] 
**max_failure_ratio** | **float** |  | [optional] 
**order** | **str** |  | 

## Example

```python
from openapi_client.models.application_update_request_update_config_swarm import ApplicationUpdateRequestUpdateConfigSwarm

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateRequestUpdateConfigSwarm from a JSON string
application_update_request_update_config_swarm_instance = ApplicationUpdateRequestUpdateConfigSwarm.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateRequestUpdateConfigSwarm.to_json())

# convert the object into a dict
application_update_request_update_config_swarm_dict = application_update_request_update_config_swarm_instance.to_dict()
# create an instance of ApplicationUpdateRequestUpdateConfigSwarm from a dict
application_update_request_update_config_swarm_from_dict = ApplicationUpdateRequestUpdateConfigSwarm.from_dict(application_update_request_update_config_swarm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


