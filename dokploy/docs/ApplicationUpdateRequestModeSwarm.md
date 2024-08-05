# ApplicationUpdateRequestModeSwarm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**replicated** | [**ApplicationUpdateRequestModeSwarmReplicated**](ApplicationUpdateRequestModeSwarmReplicated.md) |  | [optional] 
**var_global** | **object** |  | [optional] 
**replicated_job** | [**ApplicationUpdateRequestModeSwarmReplicatedJob**](ApplicationUpdateRequestModeSwarmReplicatedJob.md) |  | [optional] 
**global_job** | **object** |  | [optional] 

## Example

```python
from openapi_client.models.application_update_request_mode_swarm import ApplicationUpdateRequestModeSwarm

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateRequestModeSwarm from a JSON string
application_update_request_mode_swarm_instance = ApplicationUpdateRequestModeSwarm.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateRequestModeSwarm.to_json())

# convert the object into a dict
application_update_request_mode_swarm_dict = application_update_request_mode_swarm_instance.to_dict()
# create an instance of ApplicationUpdateRequestModeSwarm from a dict
application_update_request_mode_swarm_from_dict = ApplicationUpdateRequestModeSwarm.from_dict(application_update_request_mode_swarm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


