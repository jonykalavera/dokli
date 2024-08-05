# MariadbSaveExternalPortRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mariadb_id** | **str** |  | 
**external_port** | **float** |  | 

## Example

```python
from openapi_client.models.mariadb_save_external_port_request import MariadbSaveExternalPortRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MariadbSaveExternalPortRequest from a JSON string
mariadb_save_external_port_request_instance = MariadbSaveExternalPortRequest.from_json(json)
# print the JSON string representation of the object
print(MariadbSaveExternalPortRequest.to_json())

# convert the object into a dict
mariadb_save_external_port_request_dict = mariadb_save_external_port_request_instance.to_dict()
# create an instance of MariadbSaveExternalPortRequest from a dict
mariadb_save_external_port_request_from_dict = MariadbSaveExternalPortRequest.from_dict(mariadb_save_external_port_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


