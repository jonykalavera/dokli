# openapi_client.ApplicationApi

All URIs are relative to *https://dockploy.kalavera.xyz/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**application_clean_queues**](ApplicationApi.md#application_clean_queues) | **POST** /application.cleanQueues | 
[**application_create**](ApplicationApi.md#application_create) | **POST** /application.create | 
[**application_delete**](ApplicationApi.md#application_delete) | **POST** /application.delete | 
[**application_deploy**](ApplicationApi.md#application_deploy) | **POST** /application.deploy | 
[**application_mark_running**](ApplicationApi.md#application_mark_running) | **POST** /application.markRunning | 
[**application_one**](ApplicationApi.md#application_one) | **GET** /application.one | 
[**application_read_app_monitoring**](ApplicationApi.md#application_read_app_monitoring) | **GET** /application.readAppMonitoring | 
[**application_read_traefik_config**](ApplicationApi.md#application_read_traefik_config) | **GET** /application.readTraefikConfig | 
[**application_redeploy**](ApplicationApi.md#application_redeploy) | **POST** /application.redeploy | 
[**application_refresh_token**](ApplicationApi.md#application_refresh_token) | **POST** /application.refreshToken | 
[**application_reload**](ApplicationApi.md#application_reload) | **POST** /application.reload | 
[**application_save_build_type**](ApplicationApi.md#application_save_build_type) | **POST** /application.saveBuildType | 
[**application_save_docker_provider**](ApplicationApi.md#application_save_docker_provider) | **POST** /application.saveDockerProvider | 
[**application_save_environment**](ApplicationApi.md#application_save_environment) | **POST** /application.saveEnvironment | 
[**application_save_git_prodiver**](ApplicationApi.md#application_save_git_prodiver) | **POST** /application.saveGitProdiver | 
[**application_save_github_provider**](ApplicationApi.md#application_save_github_provider) | **POST** /application.saveGithubProvider | 
[**application_start**](ApplicationApi.md#application_start) | **POST** /application.start | 
[**application_stop**](ApplicationApi.md#application_stop) | **POST** /application.stop | 
[**application_update**](ApplicationApi.md#application_update) | **POST** /application.update | 
[**application_update_traefik_config**](ApplicationApi.md#application_update_traefik_config) | **POST** /application.updateTraefikConfig | 


# **application_clean_queues**
> application_clean_queues(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_clean_queues(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_clean_queues: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_create**
> application_create(application_create_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_create_request import ApplicationCreateRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_create_request = openapi_client.ApplicationCreateRequest() # ApplicationCreateRequest | 

    try:
        api_instance.application_create(application_create_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_create_request** | [**ApplicationCreateRequest**](ApplicationCreateRequest.md)|  | 

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

# **application_delete**
> application_delete(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_delete(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_deploy**
> application_deploy(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_deploy(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_deploy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_mark_running**
> application_mark_running(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_mark_running(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_mark_running: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_one**
> application_one(application_id)



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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_id = 'application_id_example' # str | 

    try:
        api_instance.application_one(application_id)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_one: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**|  | 

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

# **application_read_app_monitoring**
> application_read_app_monitoring(app_name)



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
    api_instance = openapi_client.ApplicationApi(api_client)
    app_name = 'app_name_example' # str | 

    try:
        api_instance.application_read_app_monitoring(app_name)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_read_app_monitoring: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_name** | **str**|  | 

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

# **application_read_traefik_config**
> application_read_traefik_config(application_id)



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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_id = 'application_id_example' # str | 

    try:
        api_instance.application_read_traefik_config(application_id)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_read_traefik_config: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_id** | **str**|  | 

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

# **application_redeploy**
> application_redeploy(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_redeploy(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_redeploy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_refresh_token**
> application_refresh_token(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_refresh_token(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_refresh_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_reload**
> application_reload(application_reload_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_reload_request import ApplicationReloadRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_reload_request = openapi_client.ApplicationReloadRequest() # ApplicationReloadRequest | 

    try:
        api_instance.application_reload(application_reload_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_reload: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_reload_request** | [**ApplicationReloadRequest**](ApplicationReloadRequest.md)|  | 

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

# **application_save_build_type**
> application_save_build_type(application_save_build_type_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_save_build_type_request import ApplicationSaveBuildTypeRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_save_build_type_request = openapi_client.ApplicationSaveBuildTypeRequest() # ApplicationSaveBuildTypeRequest | 

    try:
        api_instance.application_save_build_type(application_save_build_type_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_save_build_type: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_save_build_type_request** | [**ApplicationSaveBuildTypeRequest**](ApplicationSaveBuildTypeRequest.md)|  | 

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

# **application_save_docker_provider**
> application_save_docker_provider(application_save_docker_provider_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_save_docker_provider_request import ApplicationSaveDockerProviderRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_save_docker_provider_request = openapi_client.ApplicationSaveDockerProviderRequest() # ApplicationSaveDockerProviderRequest | 

    try:
        api_instance.application_save_docker_provider(application_save_docker_provider_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_save_docker_provider: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_save_docker_provider_request** | [**ApplicationSaveDockerProviderRequest**](ApplicationSaveDockerProviderRequest.md)|  | 

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

# **application_save_environment**
> application_save_environment(application_save_environment_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_save_environment_request import ApplicationSaveEnvironmentRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_save_environment_request = openapi_client.ApplicationSaveEnvironmentRequest() # ApplicationSaveEnvironmentRequest | 

    try:
        api_instance.application_save_environment(application_save_environment_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_save_environment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_save_environment_request** | [**ApplicationSaveEnvironmentRequest**](ApplicationSaveEnvironmentRequest.md)|  | 

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

# **application_save_git_prodiver**
> application_save_git_prodiver(application_save_git_prodiver_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_save_git_prodiver_request import ApplicationSaveGitProdiverRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_save_git_prodiver_request = openapi_client.ApplicationSaveGitProdiverRequest() # ApplicationSaveGitProdiverRequest | 

    try:
        api_instance.application_save_git_prodiver(application_save_git_prodiver_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_save_git_prodiver: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_save_git_prodiver_request** | [**ApplicationSaveGitProdiverRequest**](ApplicationSaveGitProdiverRequest.md)|  | 

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

# **application_save_github_provider**
> application_save_github_provider(application_save_github_provider_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_save_github_provider_request import ApplicationSaveGithubProviderRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_save_github_provider_request = openapi_client.ApplicationSaveGithubProviderRequest() # ApplicationSaveGithubProviderRequest | 

    try:
        api_instance.application_save_github_provider(application_save_github_provider_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_save_github_provider: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_save_github_provider_request** | [**ApplicationSaveGithubProviderRequest**](ApplicationSaveGithubProviderRequest.md)|  | 

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

# **application_start**
> application_start(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_start(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_start: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_stop**
> application_stop(application_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_delete_request import ApplicationDeleteRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_delete_request = openapi_client.ApplicationDeleteRequest() # ApplicationDeleteRequest | 

    try:
        api_instance.application_stop(application_delete_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_stop: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_delete_request** | [**ApplicationDeleteRequest**](ApplicationDeleteRequest.md)|  | 

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

# **application_update**
> application_update(application_update_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_update_request import ApplicationUpdateRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_update_request = openapi_client.ApplicationUpdateRequest() # ApplicationUpdateRequest | 

    try:
        api_instance.application_update(application_update_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_update_request** | [**ApplicationUpdateRequest**](ApplicationUpdateRequest.md)|  | 

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

# **application_update_traefik_config**
> application_update_traefik_config(application_update_traefik_config_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.application_update_traefik_config_request import ApplicationUpdateTraefikConfigRequest
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
    api_instance = openapi_client.ApplicationApi(api_client)
    application_update_traefik_config_request = openapi_client.ApplicationUpdateTraefikConfigRequest() # ApplicationUpdateTraefikConfigRequest | 

    try:
        api_instance.application_update_traefik_config(application_update_traefik_config_request)
    except Exception as e:
        print("Exception when calling ApplicationApi->application_update_traefik_config: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application_update_traefik_config_request** | [**ApplicationUpdateTraefikConfigRequest**](ApplicationUpdateTraefikConfigRequest.md)|  | 

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

