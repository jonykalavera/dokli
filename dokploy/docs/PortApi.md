# openapi_client.PortApi

All URIs are relative to *https://dockploy.kalavera.xyz/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**port_create**](PortApi.md#port_create) | **POST** /port.create | 
[**port_delete**](PortApi.md#port_delete) | **POST** /port.delete | 
[**port_one**](PortApi.md#port_one) | **GET** /port.one | 
[**port_update**](PortApi.md#port_update) | **POST** /port.update | 


# **port_create**
> port_create(port_create_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.port_create_request import PortCreateRequest
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
    api_instance = openapi_client.PortApi(api_client)
    port_create_request = openapi_client.PortCreateRequest() # PortCreateRequest | 

    try:
        api_instance.port_create(port_create_request)
    except Exception as e:
        print("Exception when calling PortApi->port_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_create_request** | [**PortCreateRequest**](PortCreateRequest.md)|  | 

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

# **port_delete**
> port_delete(port_delete_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.port_delete_request import PortDeleteRequest
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
    api_instance = openapi_client.PortApi(api_client)
    port_delete_request = openapi_client.PortDeleteRequest() # PortDeleteRequest | 

    try:
        api_instance.port_delete(port_delete_request)
    except Exception as e:
        print("Exception when calling PortApi->port_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_delete_request** | [**PortDeleteRequest**](PortDeleteRequest.md)|  | 

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

# **port_one**
> port_one(port_id)



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
    api_instance = openapi_client.PortApi(api_client)
    port_id = 'port_id_example' # str | 

    try:
        api_instance.port_one(port_id)
    except Exception as e:
        print("Exception when calling PortApi->port_one: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_id** | **str**|  | 

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

# **port_update**
> port_update(port_update_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.port_update_request import PortUpdateRequest
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
    api_instance = openapi_client.PortApi(api_client)
    port_update_request = openapi_client.PortUpdateRequest() # PortUpdateRequest | 

    try:
        api_instance.port_update(port_update_request)
    except Exception as e:
        print("Exception when calling PortApi->port_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_update_request** | [**PortUpdateRequest**](PortUpdateRequest.md)|  | 

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

