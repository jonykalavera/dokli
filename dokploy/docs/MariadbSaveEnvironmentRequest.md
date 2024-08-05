# MariadbSaveEnvironmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mariadb_id** | **str** |  | 
**env** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.mariadb_save_environment_request import MariadbSaveEnvironmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MariadbSaveEnvironmentRequest from a JSON string
mariadb_save_environment_request_instance = MariadbSaveEnvironmentRequest.from_json(json)
# print the JSON string representation of the object
print(MariadbSaveEnvironmentRequest.to_json())

# convert the object into a dict
mariadb_save_environment_request_dict = mariadb_save_environment_request_instance.to_dict()
# create an instance of MariadbSaveEnvironmentRequest from a dict
mariadb_save_environment_request_from_dict = MariadbSaveEnvironmentRequest.from_dict(mariadb_save_environment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


