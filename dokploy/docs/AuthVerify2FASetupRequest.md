# AuthVerify2FASetupRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pin** | **str** |  | 
**secret** | **str** |  | 

## Example

```python
from openapi_client.models.auth_verify2_fa_setup_request import AuthVerify2FASetupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AuthVerify2FASetupRequest from a JSON string
auth_verify2_fa_setup_request_instance = AuthVerify2FASetupRequest.from_json(json)
# print the JSON string representation of the object
print(AuthVerify2FASetupRequest.to_json())

# convert the object into a dict
auth_verify2_fa_setup_request_dict = auth_verify2_fa_setup_request_instance.to_dict()
# create an instance of AuthVerify2FASetupRequest from a dict
auth_verify2_fa_setup_request_from_dict = AuthVerify2FASetupRequest.from_dict(auth_verify2_fa_setup_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


