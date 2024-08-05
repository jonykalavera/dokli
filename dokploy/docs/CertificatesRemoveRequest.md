# CertificatesRemoveRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**certificate_id** | **str** |  | 

## Example

```python
from openapi_client.models.certificates_remove_request import CertificatesRemoveRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CertificatesRemoveRequest from a JSON string
certificates_remove_request_instance = CertificatesRemoveRequest.from_json(json)
# print the JSON string representation of the object
print(CertificatesRemoveRequest.to_json())

# convert the object into a dict
certificates_remove_request_dict = certificates_remove_request_instance.to_dict()
# create an instance of CertificatesRemoveRequest from a dict
certificates_remove_request_from_dict = CertificatesRemoveRequest.from_dict(certificates_remove_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


