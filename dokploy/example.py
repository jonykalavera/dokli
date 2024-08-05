import os

import openapi_client
from openapi_client.rest import ApiException

# Defining the host is optional and defaults to https://dockploy.kalavera.xyz/api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(host="https://dockploy.kalavera.xyz/api")

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: Authorization
configuration = openapi_client.Configuration(access_token=os.environ["BEARER_TOKEN"])


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ProjectApi(api_client)

    try:
        print("RESPONSE", api_instance.project_all_with_http_info().model_dump()["raw_data"])
    except ApiException as e:
        print(f"Exception when calling AdminApi->admin_assign_permissions: {e}\n")
