# PostgresUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**postgres_id** | **str** |  | 
**name** | **str** |  | [optional] 
**app_name** | **str** |  | [optional] 
**database_name** | **str** |  | [optional] 
**database_user** | **str** |  | [optional] 
**database_password** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**docker_image** | **str** |  | [optional] [default to 'postgres:15']
**command** | **str** |  | [optional] 
**env** | **str** |  | [optional] 
**memory_reservation** | **float** |  | [optional] 
**external_port** | **float** |  | [optional] 
**memory_limit** | **float** |  | [optional] 
**cpu_reservation** | **float** |  | [optional] 
**cpu_limit** | **float** |  | [optional] 
**application_status** | **str** |  | [optional] 
**created_at** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.postgres_update_request import PostgresUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostgresUpdateRequest from a JSON string
postgres_update_request_instance = PostgresUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(PostgresUpdateRequest.to_json())

# convert the object into a dict
postgres_update_request_dict = postgres_update_request_instance.to_dict()
# create an instance of PostgresUpdateRequest from a dict
postgres_update_request_from_dict = PostgresUpdateRequest.from_dict(postgres_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


