# CertificatesCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**certificate_id** | **str** |  | [optional] 
**name** | **str** |  | 
**certificate_data** | **str** |  | 
**private_key** | **str** |  | 
**certificate_path** | **str** |  | [optional] 
**auto_renew** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.certificates_create_request import CertificatesCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CertificatesCreateRequest from a JSON string
certificates_create_request_instance = CertificatesCreateRequest.from_json(json)
# print the JSON string representation of the object
print(CertificatesCreateRequest.to_json())

# convert the object into a dict
certificates_create_request_dict = certificates_create_request_instance.to_dict()
# create an instance of CertificatesCreateRequest from a dict
certificates_create_request_from_dict = CertificatesCreateRequest.from_dict(certificates_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


