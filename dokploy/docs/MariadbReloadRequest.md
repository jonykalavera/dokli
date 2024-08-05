# MariadbReloadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mariadb_id** | **str** |  | 
**app_name** | **str** |  | 

## Example

```python
from openapi_client.models.mariadb_reload_request import MariadbReloadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MariadbReloadRequest from a JSON string
mariadb_reload_request_instance = MariadbReloadRequest.from_json(json)
# print the JSON string representation of the object
print(MariadbReloadRequest.to_json())

# convert the object into a dict
mariadb_reload_request_dict = mariadb_reload_request_instance.to_dict()
# create an instance of MariadbReloadRequest from a dict
mariadb_reload_request_from_dict = MariadbReloadRequest.from_dict(mariadb_reload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


