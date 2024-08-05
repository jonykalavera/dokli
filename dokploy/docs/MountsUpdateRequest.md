# MountsUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mount_id** | **str** |  | 
**type** | **str** |  | [optional] 
**host_path** | **str** |  | [optional] 
**volume_name** | **str** |  | [optional] 
**file_path** | **str** |  | [optional] 
**content** | **str** |  | [optional] 
**service_type** | **str** |  | [optional] [default to 'application']
**mount_path** | **str** |  | [optional] 
**application_id** | **str** |  | [optional] 
**postgres_id** | **str** |  | [optional] 
**mariadb_id** | **str** |  | [optional] 
**mongo_id** | **str** |  | [optional] 
**mysql_id** | **str** |  | [optional] 
**redis_id** | **str** |  | [optional] 
**compose_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.mounts_update_request import MountsUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MountsUpdateRequest from a JSON string
mounts_update_request_instance = MountsUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(MountsUpdateRequest.to_json())

# convert the object into a dict
mounts_update_request_dict = mounts_update_request_instance.to_dict()
# create an instance of MountsUpdateRequest from a dict
mounts_update_request_from_dict = MountsUpdateRequest.from_dict(mounts_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


