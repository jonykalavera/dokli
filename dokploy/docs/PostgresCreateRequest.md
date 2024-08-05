# PostgresCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**app_name** | **str** |  | 
**database_name** | **str** |  | 
**database_user** | **str** |  | 
**database_password** | **str** |  | 
**docker_image** | **str** |  | [optional] [default to 'postgres:15']
**project_id** | **str** |  | 
**description** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.postgres_create_request import PostgresCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostgresCreateRequest from a JSON string
postgres_create_request_instance = PostgresCreateRequest.from_json(json)
# print the JSON string representation of the object
print(PostgresCreateRequest.to_json())

# convert the object into a dict
postgres_create_request_dict = postgres_create_request_instance.to_dict()
# create an instance of PostgresCreateRequest from a dict
postgres_create_request_from_dict = PostgresCreateRequest.from_dict(postgres_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


