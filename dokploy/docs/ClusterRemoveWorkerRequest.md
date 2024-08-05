# ClusterRemoveWorkerRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node_id** | **str** |  | 

## Example

```python
from openapi_client.models.cluster_remove_worker_request import ClusterRemoveWorkerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ClusterRemoveWorkerRequest from a JSON string
cluster_remove_worker_request_instance = ClusterRemoveWorkerRequest.from_json(json)
# print the JSON string representation of the object
print(ClusterRemoveWorkerRequest.to_json())

# convert the object into a dict
cluster_remove_worker_request_dict = cluster_remove_worker_request_instance.to_dict()
# create an instance of ClusterRemoveWorkerRequest from a dict
cluster_remove_worker_request_from_dict = ClusterRemoveWorkerRequest.from_dict(cluster_remove_worker_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


