# ComposeDeployTemplateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **str** |  | 
**id** | **str** |  | 

## Example

```python
from openapi_client.models.compose_deploy_template_request import ComposeDeployTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ComposeDeployTemplateRequest from a JSON string
compose_deploy_template_request_instance = ComposeDeployTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(ComposeDeployTemplateRequest.to_json())

# convert the object into a dict
compose_deploy_template_request_dict = compose_deploy_template_request_instance.to_dict()
# create an instance of ComposeDeployTemplateRequest from a dict
compose_deploy_template_request_from_dict = ComposeDeployTemplateRequest.from_dict(compose_deploy_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


