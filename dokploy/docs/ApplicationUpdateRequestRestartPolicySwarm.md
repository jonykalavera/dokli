# ApplicationUpdateRequestRestartPolicySwarm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition** | **str** |  | [optional] 
**delay** | **float** |  | [optional] 
**max_attempts** | **float** |  | [optional] 
**window** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.application_update_request_restart_policy_swarm import ApplicationUpdateRequestRestartPolicySwarm

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateRequestRestartPolicySwarm from a JSON string
application_update_request_restart_policy_swarm_instance = ApplicationUpdateRequestRestartPolicySwarm.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateRequestRestartPolicySwarm.to_json())

# convert the object into a dict
application_update_request_restart_policy_swarm_dict = application_update_request_restart_policy_swarm_instance.to_dict()
# create an instance of ApplicationUpdateRequestRestartPolicySwarm from a dict
application_update_request_restart_policy_swarm_from_dict = ApplicationUpdateRequestRestartPolicySwarm.from_dict(application_update_request_restart_policy_swarm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


