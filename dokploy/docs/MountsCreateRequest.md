# MountsCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**host_path** | **str** |  | [optional] 
**volume_name** | **str** |  | [optional] 
**content** | **str** |  | [optional] 
**mount_path** | **str** |  | 
**service_type** | **str** |  | [optional] [default to 'application']
**file_path** | **str** |  | [optional] 
**service_id** | **str** |  | 

## Example

```python
from openapi_client.models.mounts_create_request import MountsCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MountsCreateRequest from a JSON string
mounts_create_request_instance = MountsCreateRequest.from_json(json)
# print the JSON string representation of the object
print(MountsCreateRequest.to_json())

# convert the object into a dict
mounts_create_request_dict = mounts_create_request_instance.to_dict()
# create an instance of MountsCreateRequest from a dict
mounts_create_request_from_dict = MountsCreateRequest.from_dict(mounts_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


