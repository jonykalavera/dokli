"""API client tests."""

from dokli.api_client import APIClient, DEFAULT_TIMEOUT
from dokli.config import ConnectionConfig


def _client(mocker) -> tuple[APIClient, object]:
    connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
    session = mocker.Mock()
    response = mocker.Mock()
    response.raise_for_status.return_value = None
    session.get.return_value = response
    client = APIClient.__new__(APIClient)
    client.connection = connection
    client.session = session
    client.headers = {}
    client.base_url = "https://example.com/api/"
    return client, session


class TestRequestBody:
    """Request body handling tests."""

    def test_session_uses_bounded_timeout(self, mocker):
        """We expect the httpx session to use short timeouts so slow hosts fail fast."""
        mocker.patch("dokli.api_client.APIClient.get_open_api_document", return_value={})
        connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="echo key")
        client = APIClient(connection)
        assert client.session.timeout.connect == 5.0
        assert client.session.timeout.read == 10.0
        assert DEFAULT_TIMEOUT.connect == 5.0

    def test_sends_dict_body_as_json(self, mocker):
        """We expect dict bodies to be sent as JSON."""
        client, session = _client(mocker)
        client.request("GET", "project.all", {"body": {"name": "x"}})

        kwargs = session.get.call_args.kwargs
        assert kwargs["json"] == {"name": "x"}
        assert "data" not in kwargs

    def test_sends_list_body_as_json(self, mocker):
        """We expect list bodies to be sent as JSON."""
        client, session = _client(mocker)
        client.request("POST", "project.create", {"body": [1, 2]})

        kwargs = session.post.call_args.kwargs
        assert kwargs["json"] == [1, 2]
        assert "data" not in kwargs

    def test_sends_string_body_as_data(self, mocker):
        """We expect raw string bodies to be sent as data."""
        client, session = _client(mocker)
        client.request("POST", "project.create", {"body": "raw"})

        kwargs = session.post.call_args.kwargs
        assert kwargs["data"] == "raw"
        assert "json" not in kwargs
