# MariadbChangeStatusRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mariadb_id** | **str** |  | 
**application_status** | **str** |  | 

## Example

```python
from openapi_client.models.mariadb_change_status_request import MariadbChangeStatusRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MariadbChangeStatusRequest from a JSON string
mariadb_change_status_request_instance = MariadbChangeStatusRequest.from_json(json)
# print the JSON string representation of the object
print(MariadbChangeStatusRequest.to_json())

# convert the object into a dict
mariadb_change_status_request_dict = mariadb_change_status_request_instance.to_dict()
# create an instance of MariadbChangeStatusRequest from a dict
mariadb_change_status_request_from_dict = MariadbChangeStatusRequest.from_dict(mariadb_change_status_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


