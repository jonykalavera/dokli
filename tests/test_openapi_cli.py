"""OpenAPI CLI tests."""

from inspect import Parameter

from dokli.config import ConnectionConfig
from dokli.openapi_cli import APIRequest, HTTPMethod, _api_command_factory, _safe_param_name


class TestHTTPMethod:
    """HTTP method enumeration tests."""

    def test_parses_all_standard_methods(self):
        """We expect every standard HTTP method to be representable."""
        for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT"):
            assert HTTPMethod(method).value == method


class TestSafeParamName:
    """Safe parameter name tests."""

    def test_keeps_valid_names(self):
        """We expect valid names to be unchanged."""
        assert _safe_param_name("projectId") == "project_id"
        assert _safe_param_name("tail") == "tail"

    def test_prefixes_reserved_keywords(self):
        """We expect reserved words to be prefixed."""
        assert _safe_param_name("from") == "p_from"
        assert _safe_param_name("to") == "to"

    def test_sanitizes_invalid_characters(self):
        """We expect invalid characters to be replaced."""
        assert _safe_param_name("app-name") == "app_name"


class TestAPIClICommand:
    """Generated API command signature tests."""

    def _connection(self) -> ConnectionConfig:
        return ConnectionConfig(name="test-env", url="https://example.com", api_key="x" * 64)

    def test_required_params_stay_positional(self):
        """We expect required params to be positional arguments (no default)."""
        request = APIRequest(
            route="/docker.getContainersByAppNameMatch",
            params=[{"name": "appName", "in": "query", "required": True, "schema": {"type": "string"}}],
        )
        command = _api_command_factory(self._connection(), request)
        param = command.__signature__.parameters["app_name"]
        assert param.default is Parameter.empty

    def test_optional_params_become_flags(self):
        """We expect optional params to be --flag options defaulting to None."""
        request = APIRequest(
            route="/docker.getContainersByAppNameMatch",
            params=[
                {"name": "appType", "in": "query", "schema": {"type": "string"}},
                {"name": "appName", "in": "query", "required": True, "schema": {"type": "string"}},
            ],
        )
        command = _api_command_factory(self._connection(), request)
        app_type = command.__signature__.parameters["app_type"]
        app_name = command.__signature__.parameters["app_name"]
        assert app_type.default is None
        assert app_name.default is Parameter.empty
