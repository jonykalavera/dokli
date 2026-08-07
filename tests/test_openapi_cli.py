"""OpenAPI CLI tests."""

from dokli.openapi_cli import HTTPMethod, _safe_param_name


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
