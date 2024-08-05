# openapi_client.NotificationApi

All URIs are relative to *https://dockploy.kalavera.xyz/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**notification_all**](NotificationApi.md#notification_all) | **GET** /notification.all | 
[**notification_create_discord**](NotificationApi.md#notification_create_discord) | **POST** /notification.createDiscord | 
[**notification_create_email**](NotificationApi.md#notification_create_email) | **POST** /notification.createEmail | 
[**notification_create_slack**](NotificationApi.md#notification_create_slack) | **POST** /notification.createSlack | 
[**notification_create_telegram**](NotificationApi.md#notification_create_telegram) | **POST** /notification.createTelegram | 
[**notification_one**](NotificationApi.md#notification_one) | **GET** /notification.one | 
[**notification_remove**](NotificationApi.md#notification_remove) | **POST** /notification.remove | 
[**notification_test_discord_connection**](NotificationApi.md#notification_test_discord_connection) | **POST** /notification.testDiscordConnection | 
[**notification_test_email_connection**](NotificationApi.md#notification_test_email_connection) | **POST** /notification.testEmailConnection | 
[**notification_test_slack_connection**](NotificationApi.md#notification_test_slack_connection) | **POST** /notification.testSlackConnection | 
[**notification_test_telegram_connection**](NotificationApi.md#notification_test_telegram_connection) | **POST** /notification.testTelegramConnection | 
[**notification_update_discord**](NotificationApi.md#notification_update_discord) | **POST** /notification.updateDiscord | 
[**notification_update_email**](NotificationApi.md#notification_update_email) | **POST** /notification.updateEmail | 
[**notification_update_slack**](NotificationApi.md#notification_update_slack) | **POST** /notification.updateSlack | 
[**notification_update_telegram**](NotificationApi.md#notification_update_telegram) | **POST** /notification.updateTelegram | 


# **notification_all**
> notification_all()



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
    api_instance = openapi_client.NotificationApi(api_client)

    try:
        api_instance.notification_all()
    except Exception as e:
        print("Exception when calling NotificationApi->notification_all: %s\n" % e)
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

# **notification_create_discord**
> notification_create_discord(notification_create_discord_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_create_discord_request import NotificationCreateDiscordRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_create_discord_request = openapi_client.NotificationCreateDiscordRequest() # NotificationCreateDiscordRequest | 

    try:
        api_instance.notification_create_discord(notification_create_discord_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_create_discord: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_create_discord_request** | [**NotificationCreateDiscordRequest**](NotificationCreateDiscordRequest.md)|  | 

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

# **notification_create_email**
> notification_create_email(notification_create_email_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_create_email_request import NotificationCreateEmailRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_create_email_request = openapi_client.NotificationCreateEmailRequest() # NotificationCreateEmailRequest | 

    try:
        api_instance.notification_create_email(notification_create_email_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_create_email: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_create_email_request** | [**NotificationCreateEmailRequest**](NotificationCreateEmailRequest.md)|  | 

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

# **notification_create_slack**
> notification_create_slack(notification_create_slack_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_create_slack_request import NotificationCreateSlackRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_create_slack_request = openapi_client.NotificationCreateSlackRequest() # NotificationCreateSlackRequest | 

    try:
        api_instance.notification_create_slack(notification_create_slack_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_create_slack: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_create_slack_request** | [**NotificationCreateSlackRequest**](NotificationCreateSlackRequest.md)|  | 

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

# **notification_create_telegram**
> notification_create_telegram(notification_create_telegram_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_create_telegram_request import NotificationCreateTelegramRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_create_telegram_request = openapi_client.NotificationCreateTelegramRequest() # NotificationCreateTelegramRequest | 

    try:
        api_instance.notification_create_telegram(notification_create_telegram_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_create_telegram: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_create_telegram_request** | [**NotificationCreateTelegramRequest**](NotificationCreateTelegramRequest.md)|  | 

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

# **notification_one**
> notification_one(notification_id)



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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_id = 'notification_id_example' # str | 

    try:
        api_instance.notification_one(notification_id)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_one: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_id** | **str**|  | 

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

# **notification_remove**
> notification_remove(notification_remove_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_remove_request import NotificationRemoveRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_remove_request = openapi_client.NotificationRemoveRequest() # NotificationRemoveRequest | 

    try:
        api_instance.notification_remove(notification_remove_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_remove: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_remove_request** | [**NotificationRemoveRequest**](NotificationRemoveRequest.md)|  | 

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

# **notification_test_discord_connection**
> notification_test_discord_connection(notification_test_discord_connection_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_test_discord_connection_request import NotificationTestDiscordConnectionRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_test_discord_connection_request = openapi_client.NotificationTestDiscordConnectionRequest() # NotificationTestDiscordConnectionRequest | 

    try:
        api_instance.notification_test_discord_connection(notification_test_discord_connection_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_test_discord_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_test_discord_connection_request** | [**NotificationTestDiscordConnectionRequest**](NotificationTestDiscordConnectionRequest.md)|  | 

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

# **notification_test_email_connection**
> notification_test_email_connection(notification_test_email_connection_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_test_email_connection_request import NotificationTestEmailConnectionRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_test_email_connection_request = openapi_client.NotificationTestEmailConnectionRequest() # NotificationTestEmailConnectionRequest | 

    try:
        api_instance.notification_test_email_connection(notification_test_email_connection_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_test_email_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_test_email_connection_request** | [**NotificationTestEmailConnectionRequest**](NotificationTestEmailConnectionRequest.md)|  | 

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

# **notification_test_slack_connection**
> notification_test_slack_connection(notification_test_slack_connection_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_test_slack_connection_request import NotificationTestSlackConnectionRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_test_slack_connection_request = openapi_client.NotificationTestSlackConnectionRequest() # NotificationTestSlackConnectionRequest | 

    try:
        api_instance.notification_test_slack_connection(notification_test_slack_connection_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_test_slack_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_test_slack_connection_request** | [**NotificationTestSlackConnectionRequest**](NotificationTestSlackConnectionRequest.md)|  | 

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

# **notification_test_telegram_connection**
> notification_test_telegram_connection(notification_test_telegram_connection_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_test_telegram_connection_request import NotificationTestTelegramConnectionRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_test_telegram_connection_request = openapi_client.NotificationTestTelegramConnectionRequest() # NotificationTestTelegramConnectionRequest | 

    try:
        api_instance.notification_test_telegram_connection(notification_test_telegram_connection_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_test_telegram_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_test_telegram_connection_request** | [**NotificationTestTelegramConnectionRequest**](NotificationTestTelegramConnectionRequest.md)|  | 

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

# **notification_update_discord**
> notification_update_discord(notification_update_discord_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_update_discord_request import NotificationUpdateDiscordRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_update_discord_request = openapi_client.NotificationUpdateDiscordRequest() # NotificationUpdateDiscordRequest | 

    try:
        api_instance.notification_update_discord(notification_update_discord_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_update_discord: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_update_discord_request** | [**NotificationUpdateDiscordRequest**](NotificationUpdateDiscordRequest.md)|  | 

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

# **notification_update_email**
> notification_update_email(notification_update_email_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_update_email_request import NotificationUpdateEmailRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_update_email_request = openapi_client.NotificationUpdateEmailRequest() # NotificationUpdateEmailRequest | 

    try:
        api_instance.notification_update_email(notification_update_email_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_update_email: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_update_email_request** | [**NotificationUpdateEmailRequest**](NotificationUpdateEmailRequest.md)|  | 

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

# **notification_update_slack**
> notification_update_slack(notification_update_slack_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_update_slack_request import NotificationUpdateSlackRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_update_slack_request = openapi_client.NotificationUpdateSlackRequest() # NotificationUpdateSlackRequest | 

    try:
        api_instance.notification_update_slack(notification_update_slack_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_update_slack: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_update_slack_request** | [**NotificationUpdateSlackRequest**](NotificationUpdateSlackRequest.md)|  | 

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

# **notification_update_telegram**
> notification_update_telegram(notification_update_telegram_request)



### Example

* Bearer Authentication (Authorization):

```python
import openapi_client
from openapi_client.models.notification_update_telegram_request import NotificationUpdateTelegramRequest
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
    api_instance = openapi_client.NotificationApi(api_client)
    notification_update_telegram_request = openapi_client.NotificationUpdateTelegramRequest() # NotificationUpdateTelegramRequest | 

    try:
        api_instance.notification_update_telegram(notification_update_telegram_request)
    except Exception as e:
        print("Exception when calling NotificationApi->notification_update_telegram: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_update_telegram_request** | [**NotificationUpdateTelegramRequest**](NotificationUpdateTelegramRequest.md)|  | 

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

