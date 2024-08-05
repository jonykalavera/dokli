# ApplicationUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_id** | **str** |  | 
**name** | **str** |  | [optional] 
**app_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**env** | **str** |  | [optional] 
**build_args** | **str** |  | [optional] 
**memory_reservation** | **float** |  | [optional] 
**memory_limit** | **float** |  | [optional] 
**cpu_reservation** | **float** |  | [optional] 
**cpu_limit** | **float** |  | [optional] 
**title** | **str** |  | [optional] 
**enabled** | **bool** |  | [optional] 
**subtitle** | **str** |  | [optional] 
**command** | **str** |  | [optional] 
**refresh_token** | **str** |  | [optional] 
**source_type** | **str** |  | [optional] 
**repository** | **str** |  | [optional] 
**owner** | **str** |  | [optional] 
**branch** | **str** |  | [optional] 
**build_path** | **str** |  | [optional] 
**auto_deploy** | **bool** |  | [optional] 
**username** | **str** |  | [optional] 
**password** | **str** |  | [optional] 
**docker_image** | **str** |  | [optional] 
**custom_git_url** | **str** |  | [optional] 
**custom_git_branch** | **str** |  | [optional] 
**custom_git_build_path** | **str** |  | [optional] 
**custom_git_ssh_key_id** | **str** |  | [optional] 
**dockerfile** | **str** |  | [optional] 
**docker_context_path** | **str** |  | [optional] 
**drop_build_path** | **str** |  | [optional] 
**health_check_swarm** | [**ApplicationUpdateRequestHealthCheckSwarm**](ApplicationUpdateRequestHealthCheckSwarm.md) |  | [optional] 
**restart_policy_swarm** | [**ApplicationUpdateRequestRestartPolicySwarm**](ApplicationUpdateRequestRestartPolicySwarm.md) |  | [optional] 
**placement_swarm** | [**ApplicationUpdateRequestPlacementSwarm**](ApplicationUpdateRequestPlacementSwarm.md) |  | [optional] 
**update_config_swarm** | [**ApplicationUpdateRequestUpdateConfigSwarm**](ApplicationUpdateRequestUpdateConfigSwarm.md) |  | [optional] 
**rollback_config_swarm** | [**ApplicationUpdateRequestUpdateConfigSwarm**](ApplicationUpdateRequestUpdateConfigSwarm.md) |  | [optional] 
**mode_swarm** | [**ApplicationUpdateRequestModeSwarm**](ApplicationUpdateRequestModeSwarm.md) |  | [optional] 
**labels_swarm** | **Dict[str, str]** |  | [optional] 
**network_swarm** | [**List[ApplicationUpdateRequestNetworkSwarmInner]**](ApplicationUpdateRequestNetworkSwarmInner.md) |  | [optional] 
**replicas** | **float** |  | [optional] 
**application_status** | **str** |  | [optional] 
**build_type** | **str** |  | [optional] 
**publish_directory** | **str** |  | [optional] 
**created_at** | **str** |  | [optional] 
**registry_id** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.application_update_request import ApplicationUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicationUpdateRequest from a JSON string
application_update_request_instance = ApplicationUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ApplicationUpdateRequest.to_json())

# convert the object into a dict
application_update_request_dict = application_update_request_instance.to_dict()
# create an instance of ApplicationUpdateRequest from a dict
application_update_request_from_dict = ApplicationUpdateRequest.from_dict(application_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


