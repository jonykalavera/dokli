"""Manifest scaffolding."""

from pathlib import Path

from dokli.config import Config

TEMPLATE = """\
# Dokli as Code manifest.
#
# Describes the desired state of a Dokploy instance. Apply it with:
#   dokli validate          # offline validation against the connection's schema
#   dokli apply             # configure the instance to match this file
#   dokli plan              # preview changes first
#
# connection: name of a connection defined in your dokli config.

connection: {connection}

# Dokli manifest format version (only "v1" today).
apiVersion: v1

# Git providers are referenced by services. Credentials are write-only in
# Dokploy's API, so configure providers in the instance and resolve the
# credential at apply time via token_cmd (or DOKLI_* env vars).
#
# git_providers:
#   - name: github
#     provider: github
#     url: https://github.com
#     app_name: dokli
#     token_cmd: "secret-tool lookup dokli github"

projects: []

# Generic schema-driven resources: leaf records (domains, ports, ...) that hang
# off a service declared in "projects" above. "in" is the parent path; "data"
# holds the create/update fields. Secrets in "data" can be resolved with
# {{"cmd": "..."}} or {{"keyring": "account"}}.
#
# resources:
#   - kind: domain
#     name: www.example.com
#     in: compose:backend
#     data:
#       host: www.example.com
#       https: true
#   - kind: port
#     name: 8080
#     in: application:web
#     data:
#       publishedPort: 8080
#       targetPort: 80
#       protocol: tcp
"""


def init_manifest(config: Config, output: str = "dokploy.yaml") -> str:
    """Write a manifest template to ``output`` and return its path.

    Raises:
        FileExistsError: If the output file already exists.
    """
    path = Path(output)
    if path.exists():
        raise FileExistsError(f"{output} already exists.")
    connection = config.connections[0].name if config.connections else "<connection-name>"
    path.write_text(TEMPLATE.format(connection=connection))
    return str(path)
