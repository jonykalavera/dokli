# PostgresReloadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**postgres_id** | **str** |  | 
**app_name** | **str** |  | 

## Example

```python
from openapi_client.models.postgres_reload_request import PostgresReloadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostgresReloadRequest from a JSON string
postgres_reload_request_instance = PostgresReloadRequest.from_json(json)
# print the JSON string representation of the object
print(PostgresReloadRequest.to_json())

# convert the object into a dict
postgres_reload_request_dict = postgres_reload_request_instance.to_dict()
# create an instance of PostgresReloadRequest from a dict
postgres_reload_request_from_dict = PostgresReloadRequest.from_dict(postgres_reload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


