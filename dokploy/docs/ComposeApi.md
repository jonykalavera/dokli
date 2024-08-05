# openapi_client.ComposeApi

All URIs are relative to *https://dockploy.kalavera.xyz/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**compose_all_services**](ComposeApi.md#compose_all_services) | **GET** /compose.allServices | 
[**compose_clean_queues**](ComposeApi.md#compose_clean_queues) | **POST** /compose.cleanQueues | 
[**compose_create**](ComposeApi.md#compose_create) | **POST** /compose.create | 
[**compose_delete**](ComposeApi.md#compose_delete) | **POST** /compose.delete | 
[**compose_deploy**](ComposeApi.md#compose_deploy) | **POST** /compose.deploy | 
[**compose_deploy_template**](ComposeApi.md#compose_deploy_template) | **POST** /compose.deployTemplate | 
[**compose_get_default_command**](ComposeApi.md#compose_get_default_command) | **GET** /compose.getDefaultCommand | 
[**compose_get_tags**](ComposeApi.md#compose_get_tags) | **GET** /compose.getTags | 
[**compose_one**](ComposeApi.md#compose_one) | **GET** /compose.one | 
[**compose_randomize_compose**](ComposeApi.md#compose_randomize_compose) | **POST** /compose.randomizeCompose | 
[**compose_redeploy**](ComposeApi.md#compose_redeploy) | **POST** /compose.redeploy | 
[**compose_refresh_token**](ComposeApi.md#compose_refresh_token) | **POST** /compose.refreshToken | 
[**compose_stop**](ComposeApi.md#compose_stop) | **POST** /compose.stop | 
[**compose_templates**](ComposeApi.md#compose_templates) | **GET** /compose.templates | 
[**compose_update**](ComposeApi.md#compose_update) | **POST** /compose.update | 


# **compose_all_services**
> compose_all_services(compose_id)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_id = 'compose_id_example' # str | 

    try:
        api_instance.compose_all_services(compose_id)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_all_services: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_clean_queues**
> compose_clean_queues(compose_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_delete_request import ComposeDeleteRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_delete_request = openapi_client.ComposeDeleteRequest() # ComposeDeleteRequest | 

    try:
        api_instance.compose_clean_queues(compose_delete_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_clean_queues: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_delete_request** | [**ComposeDeleteRequest**](ComposeDeleteRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_create**
> compose_create(compose_create_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_create_request import ComposeCreateRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_create_request = openapi_client.ComposeCreateRequest() # ComposeCreateRequest | 

    try:
        api_instance.compose_create(compose_create_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_create_request** | [**ComposeCreateRequest**](ComposeCreateRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_delete**
> compose_delete(compose_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_delete_request import ComposeDeleteRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_delete_request = openapi_client.ComposeDeleteRequest() # ComposeDeleteRequest | 

    try:
        api_instance.compose_delete(compose_delete_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_delete_request** | [**ComposeDeleteRequest**](ComposeDeleteRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_deploy**
> compose_deploy(compose_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_delete_request import ComposeDeleteRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_delete_request = openapi_client.ComposeDeleteRequest() # ComposeDeleteRequest | 

    try:
        api_instance.compose_deploy(compose_delete_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_deploy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_delete_request** | [**ComposeDeleteRequest**](ComposeDeleteRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_deploy_template**
> compose_deploy_template(compose_deploy_template_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_deploy_template_request import ComposeDeployTemplateRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_deploy_template_request = openapi_client.ComposeDeployTemplateRequest() # ComposeDeployTemplateRequest | 

    try:
        api_instance.compose_deploy_template(compose_deploy_template_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_deploy_template: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_deploy_template_request** | [**ComposeDeployTemplateRequest**](ComposeDeployTemplateRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_get_default_command**
> compose_get_default_command(compose_id)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_id = 'compose_id_example' # str | 

    try:
        api_instance.compose_get_default_command(compose_id)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_get_default_command: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_get_tags**
> compose_get_tags()



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)

    try:
        api_instance.compose_get_tags()
    except Exception as e:
        print("Exception when calling ComposeApi->compose_get_tags: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_one**
> compose_one(compose_id)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_id = 'compose_id_example' # str | 

    try:
        api_instance.compose_one(compose_id)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_one: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_randomize_compose**
> compose_randomize_compose(compose_randomize_compose_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_randomize_compose_request import ComposeRandomizeComposeRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_randomize_compose_request = openapi_client.ComposeRandomizeComposeRequest() # ComposeRandomizeComposeRequest | 

    try:
        api_instance.compose_randomize_compose(compose_randomize_compose_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_randomize_compose: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_randomize_compose_request** | [**ComposeRandomizeComposeRequest**](ComposeRandomizeComposeRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_redeploy**
> compose_redeploy(compose_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_delete_request import ComposeDeleteRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_delete_request = openapi_client.ComposeDeleteRequest() # ComposeDeleteRequest | 

    try:
        api_instance.compose_redeploy(compose_delete_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_redeploy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_delete_request** | [**ComposeDeleteRequest**](ComposeDeleteRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_refresh_token**
> compose_refresh_token(compose_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_delete_request import ComposeDeleteRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_delete_request = openapi_client.ComposeDeleteRequest() # ComposeDeleteRequest | 

    try:
        api_instance.compose_refresh_token(compose_delete_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_refresh_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_delete_request** | [**ComposeDeleteRequest**](ComposeDeleteRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_stop**
> compose_stop(compose_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_delete_request import ComposeDeleteRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_delete_request = openapi_client.ComposeDeleteRequest() # ComposeDeleteRequest | 

    try:
        api_instance.compose_stop(compose_delete_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_stop: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_delete_request** | [**ComposeDeleteRequest**](ComposeDeleteRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_templates**
> compose_templates()



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)

    try:
        api_instance.compose_templates()
    except Exception as e:
        print("Exception when calling ComposeApi->compose_templates: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compose_update**
> compose_update(compose_update_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.compose_update_request import ComposeUpdateRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://dockploy.kalavera.xyz/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ComposeApi(api_client)
    compose_update_request = openapi_client.ComposeUpdateRequest() # ComposeUpdateRequest | 

    try:
        api_instance.compose_update(compose_update_request)
    except Exception as e:
        print("Exception when calling ComposeApi->compose_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compose_update_request** | [**ComposeUpdateRequest**](ComposeUpdateRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

[Authorization](../README.md#Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

