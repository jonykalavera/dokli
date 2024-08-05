# PostgresSaveEnvironmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**postgres_id** | **str** |  | 
**env** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.postgres_save_environment_request import PostgresSaveEnvironmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostgresSaveEnvironmentRequest from a JSON string
postgres_save_environment_request_instance = PostgresSaveEnvironmentRequest.from_json(json)
# print the JSON string representation of the object
print(PostgresSaveEnvironmentRequest.to_json())

# convert the object into a dict
postgres_save_environment_request_dict = postgres_save_environment_request_instance.to_dict()
# create an instance of PostgresSaveEnvironmentRequest from a dict
postgres_save_environment_request_from_dict = PostgresSaveEnvironmentRequest.from_dict(postgres_save_environment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


