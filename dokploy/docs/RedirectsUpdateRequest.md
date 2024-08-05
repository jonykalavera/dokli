# RedirectsUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**redirect_id** | **str** |  | 
**regex** | **str** |  | 
**replacement** | **str** |  | 
**permanent** | **bool** |  | 

## Example

```python
from openapi_client.models.redirects_update_request import RedirectsUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RedirectsUpdateRequest from a JSON string
redirects_update_request_instance = RedirectsUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(RedirectsUpdateRequest.to_json())

# convert the object into a dict
redirects_update_request_dict = redirects_update_request_instance.to_dict()
# create an instance of RedirectsUpdateRequest from a dict
redirects_update_request_from_dict = RedirectsUpdateRequest.from_dict(redirects_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


