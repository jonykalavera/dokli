"""The ``dokli doctor`` command: quick instance health checks."""

import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from dokli.api_client import DEFAULT_TIMEOUT
from dokli.config import ConnectionConfig

#: A schema cache older than this many days is reported as stale.
STALE_AFTER_DAYS = 7


@dataclass
class CheckResult:
    """One health check outcome."""

    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, str | bool]:
        """Serializable dict for JSON output."""
        return {"check": self.name, "ok": self.ok, "detail": self.detail}


@dataclass
class DoctorReport:
    """The result of running every health check for a connection."""

    connection: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether every check passed."""
        return all(check.ok for check in self.checks)

    def to_dict(self) -> dict[str, object]:
        """Serializable dict for JSON output."""
        return {"connection": self.connection, "ok": self.ok, "checks": [c.to_dict() for c in self.checks]}


def _cache_path(connection: ConnectionConfig) -> Path:
    return Path.home() / ".config/dokli/cache" / f"{connection.name}.openapi.json"


def _client() -> httpx.Client:
    """A short-timeout client matching the API client's TLS behavior."""
    return httpx.Client(verify=False, follow_redirects=True, timeout=DEFAULT_TIMEOUT)


def check_connectivity(connection: ConnectionConfig) -> CheckResult:
    """Reach the instance's web root (no auth needed)."""
    try:
        with _client() as client:
            response = client.get(f"{connection.url}/")
        return CheckResult("connectivity", True, f"HTTP {response.status_code}")
    except httpx.HTTPError as err:
        return CheckResult("connectivity", False, str(err))


def check_auth(connection: ConnectionConfig) -> CheckResult:
    """Call ``settings.health`` with the resolved API key."""
    try:
        api_key = connection.get_api_key()
    except Exception as err:  # noqa: BLE001 - key resolution may fail in many ways.
        return CheckResult("auth", False, f"api key resolution failed: {err}")
    try:
        with _client() as client:
            response = client.get(
                f"{connection.url}/api/settings.health",
                headers={"x-api-key": api_key, "accept": "application/json"},
            )
        if response.status_code == 200:
            return CheckResult("auth", True, "api key accepted")
        return CheckResult("auth", False, f"HTTP {response.status_code}")
    except httpx.HTTPError as err:
        return CheckResult("auth", False, str(err))


def check_schema_cache(connection: ConnectionConfig) -> CheckResult:
    """The cached OpenAPI schema exists and is not stale."""
    path = _cache_path(connection)
    if not path.exists():
        return CheckResult("schema", False, "cache missing — run `dokli refresh`")
    age_days = (time.time() - path.stat().st_mtime) / 86400
    if age_days > STALE_AFTER_DAYS:
        return CheckResult("schema", False, f"stale ({age_days:.0f}d old) — run `dokli refresh`")
    return CheckResult("schema", True, f"{age_days:.0f}d old")


def run_doctor(connection: ConnectionConfig) -> DoctorReport:
    """Run every health check for a connection, in order."""
    report = DoctorReport(connection=connection.name)
    for check in (check_connectivity, check_auth, check_schema_cache):
        report.checks.append(check(connection))
    return report
