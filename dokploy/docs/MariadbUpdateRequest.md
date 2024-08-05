# MariadbUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mariadb_id** | **str** |  | 
**name** | **str** |  | [optional] 
**app_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**database_name** | **str** |  | [optional] 
**database_user** | **str** |  | [optional] 
**database_password** | **str** |  | [optional] 
**database_root_password** | **str** |  | [optional] 
**docker_image** | **str** |  | [optional] [default to 'mariadb:6']
**command** | **str** |  | [optional] 
**env** | **str** |  | [optional] 
**memory_reservation** | **float** |  | [optional] 
**memory_limit** | **float** |  | [optional] 
**cpu_reservation** | **float** |  | [optional] 
**cpu_limit** | **float** |  | [optional] 
**external_port** | **float** |  | [optional] 
**application_status** | **str** |  | [optional] 
**created_at** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.mariadb_update_request import MariadbUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MariadbUpdateRequest from a JSON string
mariadb_update_request_instance = MariadbUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(MariadbUpdateRequest.to_json())

# convert the object into a dict
mariadb_update_request_dict = mariadb_update_request_instance.to_dict()
# create an instance of MariadbUpdateRequest from a dict
mariadb_update_request_from_dict = MariadbUpdateRequest.from_dict(mariadb_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


