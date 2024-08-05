# openapi_client.DestinationApi

All URIs are relative to *https://dockploy.kalavera.xyz/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**destination_all**](DestinationApi.md#destination_all) | **GET** /destination.all | 
[**destination_create**](DestinationApi.md#destination_create) | **POST** /destination.create | 
[**destination_one**](DestinationApi.md#destination_one) | **GET** /destination.one | 
[**destination_remove**](DestinationApi.md#destination_remove) | **POST** /destination.remove | 
[**destination_test_connection**](DestinationApi.md#destination_test_connection) | **POST** /destination.testConnection | 
[**destination_update**](DestinationApi.md#destination_update) | **POST** /destination.update | 


# **destination_all**
> destination_all()



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
    api_instance = openapi_client.DestinationApi(api_client)

    try:
        api_instance.destination_all()
    except Exception as e:
        print("Exception when calling DestinationApi->destination_all: %s\n" % e)
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

# **destination_create**
> destination_create(destination_create_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.destination_create_request import DestinationCreateRequest
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
    api_instance = openapi_client.DestinationApi(api_client)
    destination_create_request = openapi_client.DestinationCreateRequest() # DestinationCreateRequest | 

    try:
        api_instance.destination_create(destination_create_request)
    except Exception as e:
        print("Exception when calling DestinationApi->destination_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_create_request** | [**DestinationCreateRequest**](DestinationCreateRequest.md)|  | 

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

# **destination_one**
> destination_one(destination_id)



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
    api_instance = openapi_client.DestinationApi(api_client)
    destination_id = 'destination_id_example' # str | 

    try:
        api_instance.destination_one(destination_id)
    except Exception as e:
        print("Exception when calling DestinationApi->destination_one: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_id** | **str**|  | 

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

# **destination_remove**
> destination_remove(destination_remove_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.destination_remove_request import DestinationRemoveRequest
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
    api_instance = openapi_client.DestinationApi(api_client)
    destination_remove_request = openapi_client.DestinationRemoveRequest() # DestinationRemoveRequest | 

    try:
        api_instance.destination_remove(destination_remove_request)
    except Exception as e:
        print("Exception when calling DestinationApi->destination_remove: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_remove_request** | [**DestinationRemoveRequest**](DestinationRemoveRequest.md)|  | 

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

# **destination_test_connection**
> destination_test_connection(destination_create_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.destination_create_request import DestinationCreateRequest
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
    api_instance = openapi_client.DestinationApi(api_client)
    destination_create_request = openapi_client.DestinationCreateRequest() # DestinationCreateRequest | 

    try:
        api_instance.destination_test_connection(destination_create_request)
    except Exception as e:
        print("Exception when calling DestinationApi->destination_test_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_create_request** | [**DestinationCreateRequest**](DestinationCreateRequest.md)|  | 

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

# **destination_update**
> destination_update(destination_update_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.destination_update_request import DestinationUpdateRequest
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
    api_instance = openapi_client.DestinationApi(api_client)
    destination_update_request = openapi_client.DestinationUpdateRequest() # DestinationUpdateRequest | 

    try:
        api_instance.destination_update(destination_update_request)
    except Exception as e:
        print("Exception when calling DestinationApi->destination_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_update_request** | [**DestinationUpdateRequest**](DestinationUpdateRequest.md)|  | 

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

