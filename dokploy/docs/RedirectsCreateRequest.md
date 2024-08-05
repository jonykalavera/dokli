# RedirectsCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**regex** | **str** |  | 
**replacement** | **str** |  | 
**permanent** | **bool** |  | 
**application_id** | **str** |  | 

## Example

```python
from openapi_client.models.redirects_create_request import RedirectsCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedirectsCreateRequest from a JSON string
redirects_create_request_instance = RedirectsCreateRequest.from_json(json)
# print the JSON string representation of the object
print(RedirectsCreateRequest.to_json())

# convert the object into a dict
redirects_create_request_dict = redirects_create_request_instance.to_dict()
# create an instance of RedirectsCreateRequest from a dict
redirects_create_request_from_dict = RedirectsCreateRequest.from_dict(redirects_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


