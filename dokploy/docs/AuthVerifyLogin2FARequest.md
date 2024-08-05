# AuthVerifyLogin2FARequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pin** | **str** |  | 
**id** | **str** |  | 

## Example

```python
from openapi_client.models.auth_verify_login2_fa_request import AuthVerifyLogin2FARequest

# TODO update the JSON string below
json = "{}"
# create an instance of AuthVerifyLogin2FARequest from a JSON string
auth_verify_login2_fa_request_instance = AuthVerifyLogin2FARequest.from_json(json)
# print the JSON string representation of the object
print(AuthVerifyLogin2FARequest.to_json())

# convert the object into a dict
auth_verify_login2_fa_request_dict = auth_verify_login2_fa_request_instance.to_dict()
# create an instance of AuthVerifyLogin2FARequest from a dict
auth_verify_login2_fa_request_from_dict = AuthVerifyLogin2FARequest.from_dict(auth_verify_login2_fa_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


