# PostgresChangeStatusRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**postgres_id** | **str** |  | 
**application_status** | **str** |  | 

## Example

```python
from openapi_client.models.postgres_change_status_request import PostgresChangeStatusRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostgresChangeStatusRequest from a JSON string
postgres_change_status_request_instance = PostgresChangeStatusRequest.from_json(json)
# print the JSON string representation of the object
print(PostgresChangeStatusRequest.to_json())

# convert the object into a dict
postgres_change_status_request_dict = postgres_change_status_request_instance.to_dict()
# create an instance of PostgresChangeStatusRequest from a dict
postgres_change_status_request_from_dict = PostgresChangeStatusRequest.from_dict(postgres_change_status_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


