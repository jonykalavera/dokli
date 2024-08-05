# MariadbCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**app_name** | **str** |  | 
**docker_image** | **str** |  | [optional] [default to 'mariadb:6']
**database_root_password** | **str** |  | 
**project_id** | **str** |  | 
**description** | **str** |  | [optional] 
**database_name** | **str** |  | 
**database_user** | **str** |  | 
**database_password** | **str** |  | 

## Example

```python
from openapi_client.models.mariadb_create_request import MariadbCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MariadbCreateRequest from a JSON string
mariadb_create_request_instance = MariadbCreateRequest.from_json(json)
# print the JSON string representation of the object
print(MariadbCreateRequest.to_json())

# convert the object into a dict
mariadb_create_request_dict = mariadb_create_request_instance.to_dict()
# create an instance of MariadbCreateRequest from a dict
mariadb_create_request_from_dict = MariadbCreateRequest.from_dict(mariadb_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


