"""Doctor (health checks) tests."""

import time
from pathlib import Path

import httpx

from dokli.config import ConnectionConfig
from dokli.doctor import (
    STALE_AFTER_DAYS,
    CheckResult,
    DoctorReport,
    check_auth,
    check_connectivity,
    check_schema_cache,
    run_doctor,
)


def _connection() -> ConnectionConfig:
    return ConnectionConfig(name="test-env", url="https://example.com", api_key="x" * 64)


def _client_mock(mocker, **kwargs):
    """A mock httpx.Client usable as a context manager (``with _client()``)."""
    client = mocker.MagicMock(**kwargs)
    client.__enter__.return_value = client
    return client


class TestCheckConnectivity:
    """Connectivity check tests."""

    def test_reports_ok_on_any_http_response(self, mocker):
        """We expect any HTTP response to prove connectivity."""
        response = mocker.Mock(status_code=200)
        client = _client_mock(mocker)
        client.get.return_value = response
        mocker.patch("dokli.doctor._client", return_value=client)
        check = check_connectivity(_connection())
        assert check.ok
        assert check.detail == "HTTP 200"

    def test_reports_failure_on_http_error(self, mocker):
        """We expect an httpx error to fail the check."""
        client = _client_mock(mocker)
        client.get.side_effect = httpx.ConnectError("boom")
        mocker.patch("dokli.doctor._client", return_value=client)
        check = check_connectivity(_connection())
        assert not check.ok
        assert "boom" in check.detail


class TestCheckAuth:
    """Auth check tests."""

    def test_ok_on_200(self, mocker):
        """We expect a 200 from settings.health to pass."""
        response = mocker.Mock(status_code=200)
        client = _client_mock(mocker)
        client.get.return_value = response
        mocker.patch("dokli.doctor._client", return_value=client)
        check = check_auth(_connection())
        assert check.ok
        assert check.detail == "api key accepted"

    def test_fails_on_401(self, mocker):
        """We expect a 401 (bad key) to fail."""
        response = mocker.Mock(status_code=401)
        client = _client_mock(mocker)
        client.get.return_value = response
        mocker.patch("dokli.doctor._client", return_value=client)
        check = check_auth(_connection())
        assert not check.ok
        assert check.detail == "HTTP 401"

    def test_fails_when_key_resolution_fails(self, mocker):
        """We expect a failing api_key_cmd to fail the auth check."""
        connection = ConnectionConfig(name="test-env", url="https://example.com", api_key_cmd="false")
        check = check_auth(connection)
        assert not check.ok
        assert "api key resolution failed" in check.detail


class TestCheckSchemaCache:
    """Schema cache freshness check tests."""

    def test_missing_cache_fails(self, mocker):
        """We expect a missing cache file to fail."""
        mocker.patch("dokli.doctor._cache_path", return_value=Path("/nonexistent/cache.json"))
        check = check_schema_cache(_connection())
        assert not check.ok
        assert "cache missing" in check.detail

    def test_fresh_cache_ok(self, mocker):
        """We expect a recent cache file to pass."""
        cache = mocker.Mock()
        cache.exists.return_value = True
        cache.stat.return_value = mocker.Mock(st_mtime=time.time())
        mocker.patch("dokli.doctor._cache_path", return_value=cache)
        check = check_schema_cache(_connection())
        assert check.ok

    def test_stale_cache_fails(self, mocker):
        """We expect a cache older than STALE_AFTER_DAYS to fail."""
        cache = mocker.Mock()
        cache.exists.return_value = True
        cache.stat.return_value = mocker.Mock(st_mtime=time.time() - (STALE_AFTER_DAYS + 1) * 86400)
        mocker.patch("dokli.doctor._cache_path", return_value=cache)
        check = check_schema_cache(_connection())
        assert not check.ok
        assert "stale" in check.detail


class TestRunDoctor:
    """Report aggregation tests."""

    def test_all_ok_report(self, mocker):
        """We expect run_doctor to aggregate passing checks."""
        mocker.patch("dokli.doctor.check_connectivity", return_value=_ok("connectivity"))
        mocker.patch("dokli.doctor.check_auth", return_value=_ok("auth"))
        mocker.patch("dokli.doctor.check_schema_cache", return_value=_ok("schema"))
        report = run_doctor(_connection())
        assert report.ok
        assert [c.name for c in report.checks] == ["connectivity", "auth", "schema"]

    def test_any_failure_flags_report(self, mocker):
        """We expect a failing check to flag the whole report."""
        mocker.patch("dokli.doctor.check_connectivity", return_value=_ok("connectivity"))
        mocker.patch("dokli.doctor.check_auth", return_value=_fail("auth"))
        mocker.patch("dokli.doctor.check_schema_cache", return_value=_ok("schema"))
        report = run_doctor(_connection())
        assert not report.ok


def _ok(name: str):
    return CheckResult(name, True, "ok")


def _fail(name: str):
    return CheckResult(name, False, "boom")


class TestDoctorReport:
    """Report serialization tests."""

    def test_to_dict(self):
        """We expect to_dict to flatten checks."""
        report = DoctorReport(connection="test-env", checks=[_ok("connectivity"), _fail("auth")])
        data = report.to_dict()
        assert data["connection"] == "test-env"
        assert data["ok"] is False
        assert data["checks"][0] == {"check": "connectivity", "ok": True, "detail": "ok"}
