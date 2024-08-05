# openapi_client.MongoApi

All URIs are relative to *https://dockploy.kalavera.xyz/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**mongo_change_status**](MongoApi.md#mongo_change_status) | **POST** /mongo.changeStatus | 
[**mongo_create**](MongoApi.md#mongo_create) | **POST** /mongo.create | 
[**mongo_deploy**](MongoApi.md#mongo_deploy) | **POST** /mongo.deploy | 
[**mongo_one**](MongoApi.md#mongo_one) | **GET** /mongo.one | 
[**mongo_reload**](MongoApi.md#mongo_reload) | **POST** /mongo.reload | 
[**mongo_remove**](MongoApi.md#mongo_remove) | **POST** /mongo.remove | 
[**mongo_save_environment**](MongoApi.md#mongo_save_environment) | **POST** /mongo.saveEnvironment | 
[**mongo_save_external_port**](MongoApi.md#mongo_save_external_port) | **POST** /mongo.saveExternalPort | 
[**mongo_start**](MongoApi.md#mongo_start) | **POST** /mongo.start | 
[**mongo_stop**](MongoApi.md#mongo_stop) | **POST** /mongo.stop | 
[**mongo_update**](MongoApi.md#mongo_update) | **POST** /mongo.update | 


# **mongo_change_status**
> mongo_change_status(mongo_change_status_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_change_status_request import MongoChangeStatusRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_change_status_request = openapi_client.MongoChangeStatusRequest() # MongoChangeStatusRequest | 

    try:
        api_instance.mongo_change_status(mongo_change_status_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_change_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_change_status_request** | [**MongoChangeStatusRequest**](MongoChangeStatusRequest.md)|  | 

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

# **mongo_create**
> mongo_create(mongo_create_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_create_request import MongoCreateRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_create_request = openapi_client.MongoCreateRequest() # MongoCreateRequest | 

    try:
        api_instance.mongo_create(mongo_create_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_create_request** | [**MongoCreateRequest**](MongoCreateRequest.md)|  | 

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

# **mongo_deploy**
> mongo_deploy(mongo_start_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_start_request import MongoStartRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_start_request = openapi_client.MongoStartRequest() # MongoStartRequest | 

    try:
        api_instance.mongo_deploy(mongo_start_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_deploy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_start_request** | [**MongoStartRequest**](MongoStartRequest.md)|  | 

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

# **mongo_one**
> mongo_one(mongo_id)



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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_id = 'mongo_id_example' # str | 

    try:
        api_instance.mongo_one(mongo_id)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_one: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_id** | **str**|  | 

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

# **mongo_reload**
> mongo_reload(mongo_reload_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_reload_request import MongoReloadRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_reload_request = openapi_client.MongoReloadRequest() # MongoReloadRequest | 

    try:
        api_instance.mongo_reload(mongo_reload_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_reload: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_reload_request** | [**MongoReloadRequest**](MongoReloadRequest.md)|  | 

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

# **mongo_remove**
> mongo_remove(mongo_start_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_start_request import MongoStartRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_start_request = openapi_client.MongoStartRequest() # MongoStartRequest | 

    try:
        api_instance.mongo_remove(mongo_start_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_remove: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_start_request** | [**MongoStartRequest**](MongoStartRequest.md)|  | 

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

# **mongo_save_environment**
> mongo_save_environment(mongo_save_environment_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_save_environment_request import MongoSaveEnvironmentRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_save_environment_request = openapi_client.MongoSaveEnvironmentRequest() # MongoSaveEnvironmentRequest | 

    try:
        api_instance.mongo_save_environment(mongo_save_environment_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_save_environment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_save_environment_request** | [**MongoSaveEnvironmentRequest**](MongoSaveEnvironmentRequest.md)|  | 

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

# **mongo_save_external_port**
> mongo_save_external_port(mongo_save_external_port_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_save_external_port_request import MongoSaveExternalPortRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_save_external_port_request = openapi_client.MongoSaveExternalPortRequest() # MongoSaveExternalPortRequest | 

    try:
        api_instance.mongo_save_external_port(mongo_save_external_port_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_save_external_port: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_save_external_port_request** | [**MongoSaveExternalPortRequest**](MongoSaveExternalPortRequest.md)|  | 

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

# **mongo_start**
> mongo_start(mongo_start_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_start_request import MongoStartRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_start_request = openapi_client.MongoStartRequest() # MongoStartRequest | 

    try:
        api_instance.mongo_start(mongo_start_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_start: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_start_request** | [**MongoStartRequest**](MongoStartRequest.md)|  | 

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

# **mongo_stop**
> mongo_stop(mongo_start_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_start_request import MongoStartRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_start_request = openapi_client.MongoStartRequest() # MongoStartRequest | 

    try:
        api_instance.mongo_stop(mongo_start_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_stop: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_start_request** | [**MongoStartRequest**](MongoStartRequest.md)|  | 

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

# **mongo_update**
> mongo_update(mongo_update_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.mongo_update_request import MongoUpdateRequest
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
    api_instance = openapi_client.MongoApi(api_client)
    mongo_update_request = openapi_client.MongoUpdateRequest() # MongoUpdateRequest | 

    try:
        api_instance.mongo_update(mongo_update_request)
    except Exception as e:
        print("Exception when calling MongoApi->mongo_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mongo_update_request** | [**MongoUpdateRequest**](MongoUpdateRequest.md)|  | 

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

