# ApplicationUpdateRequestHealthCheckSwarm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test** | **List[str]** |  | [optional] 
**interval** | **float** |  | [optional] 
**timeout** | **float** |  | [optional] 
**start_period** | **float** |  | [optional] 
**retries** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.application_update_request_health_check_swarm import ApplicationUpdateRequestHealthCheckSwarm

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateRequestHealthCheckSwarm from a JSON string
application_update_request_health_check_swarm_instance = ApplicationUpdateRequestHealthCheckSwarm.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateRequestHealthCheckSwarm.to_json())

# convert the object into a dict
application_update_request_health_check_swarm_dict = application_update_request_health_check_swarm_instance.to_dict()
# create an instance of ApplicationUpdateRequestHealthCheckSwarm from a dict
application_update_request_health_check_swarm_from_dict = ApplicationUpdateRequestHealthCheckSwarm.from_dict(application_update_request_health_check_swarm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


