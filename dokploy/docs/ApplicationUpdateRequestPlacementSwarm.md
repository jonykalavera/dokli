# ApplicationUpdateRequestPlacementSwarm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**constraints** | **List[str]** |  | [optional] 
**preferences** | [**List[ApplicationUpdateRequestPlacementSwarmPreferencesInner]**](ApplicationUpdateRequestPlacementSwarmPreferencesInner.md) |  | [optional] 
**max_replicas** | **float** |  | [optional] 
**platforms** | [**List[ApplicationUpdateRequestPlacementSwarmPlatformsInner]**](ApplicationUpdateRequestPlacementSwarmPlatformsInner.md) |  | [optional] 

## Example

```python
from openapi_client.models.application_update_request_placement_swarm import ApplicationUpdateRequestPlacementSwarm

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateRequestPlacementSwarm from a JSON string
application_update_request_placement_swarm_instance = ApplicationUpdateRequestPlacementSwarm.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateRequestPlacementSwarm.to_json())

# convert the object into a dict
application_update_request_placement_swarm_dict = application_update_request_placement_swarm_instance.to_dict()
# create an instance of ApplicationUpdateRequestPlacementSwarm from a dict
application_update_request_placement_swarm_from_dict = ApplicationUpdateRequestPlacementSwarm.from_dict(application_update_request_placement_swarm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


