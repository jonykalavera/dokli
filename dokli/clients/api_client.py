"""API client for Dokli."""

import json
from pathlib import Path
from typing import Any

import httpx

from dokli.config import ConnectionConfig


class APIClient:
    """Dokploy API client."""

    def __init__(self, connection: ConnectionConfig, cache_path: str | None = None, force_refresh=False):
        """Initialize the API client."""
        _base_url = str(connection.url).rstrip("/")
        self.connection = connection
        self.force_refresh = force_refresh
        self.cache_path = Path(cache_path) if cache_path else Path.home() / ".config/dokli/cache"
        self.base_url = f"{_base_url}/api/"
        self.headers = {
            "Authorization": f"Bearer {connection.api_key.get_secret_value()}",
            "accept": "application/json",
        }
        self.session = httpx.Client(verify=False, follow_redirects=True)
        self.schema = self.get_open_api_document()

    def _get_cache_path(self):
        return self.cache_path / f"{self.connection.name}.openapi.json"

    def _get_open_api_document_cache(self):
        cache_path = self._get_cache_path()
        if not cache_path.exists():
            return None
        return json.loads(cache_path.read_text())

    def _set_open_api_document_cache(self, schema):
        cache_path = self._get_cache_path()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(schema))

    def _get_open_api_document(self):
        response = self.request(method="GET", path="settings.getOpenApiDocument", params={})
        response.raise_for_status()
        return response.json()

    def get_open_api_document(self):
        """Retrieve OpenAPI document for the connection."""
        schema = self._get_open_api_document_cache()
        if not schema or self.force_refresh:
            schema = self._get_open_api_document()
            self._set_open_api_document_cache(schema)
        return schema

    def request(self, method: str, path: str, params: dict[str, Any]) -> httpx.Response:
        """Send a request to the API."""
        query_params = {}
        path_params = {}
        body = params.pop("body", None)

        for key, value in params.items():
            if key in path:
                path_params[key] = value
            else:
                query_params[key] = value

        formatted_path = path.format(**path_params)

        response = getattr(self.session, method.lower())(
            url=f"{self.base_url}{formatted_path}",
            params=query_params,
            headers=self.headers,
            **({"data": body} if body else {}),
        )
        response.raise_for_status()
        return response
