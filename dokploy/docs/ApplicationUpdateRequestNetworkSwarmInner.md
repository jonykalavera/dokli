# ApplicationUpdateRequestNetworkSwarmInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target** | **str** |  | [optional] 
**aliases** | **List[str]** |  | [optional] 
**driver_opts** | **object** |  | [optional] 

## Example

```python
from openapi_client.models.application_update_request_network_swarm_inner import ApplicationUpdateRequestNetworkSwarmInner

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateRequestNetworkSwarmInner from a JSON string
application_update_request_network_swarm_inner_instance = ApplicationUpdateRequestNetworkSwarmInner.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateRequestNetworkSwarmInner.to_json())

# convert the object into a dict
application_update_request_network_swarm_inner_dict = application_update_request_network_swarm_inner_instance.to_dict()
# create an instance of ApplicationUpdateRequestNetworkSwarmInner from a dict
application_update_request_network_swarm_inner_from_dict = ApplicationUpdateRequestNetworkSwarmInner.from_dict(application_update_request_network_swarm_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


