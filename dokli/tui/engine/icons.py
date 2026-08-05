"""Nerd Font icons for Dokploy entities."""

ENTITY_ICONS = {
    "project": "\uf07b",  # fa-folder
    "compose": "\uf308",  # fa-docker
    "application": "\uf135",  # fa-rocket
    "postgres": "\ue76e",  # dev-postgresql
    "mysql": "\ue704",  # dev-mysql
    "mariadb": "\ue704",  # dev-mysql
    "mongo": "\ue7a4",  # dev-mongodb
    "redis": "\ue76d",  # dev-redis
    "libsql": "\uf1c0",  # fa-database
    "server": "\uf233",  # fa-server
    "domain": "\uf0ac",  # fa-globe
    "deployment": "\uf085",  # fa-cogs
    "user": "\uf2bd",  # fa-user-circle
    "notification": "\uf0f3",  # fa-bell
    "backup": "\uf0c7",  # fa-save
    "sshKey": "\uf084",  # fa-key
    "environment": "\uf1b2",  # fa-cube
    "docker": "\uf308",  # fa-docker
    "registry": "\uf466",  # fa-box
    "tag": "\uf02b",  # fa-tag
    "organization": "\uf1ad",  # fa-building
    "certificate": "\uf0a3",  # fa-certificate
    "settings": "\uf013",  # fa-cog
    "port": "\uf1e6",  # fa-plug
    "mount": "\uf0c6",  # fa-paperclip
    "gitea": "\ue618",  # dev-git
    "github": "\ue707",  # dev-github
    "gitlab": "\ue696",  # dev-gitlab
    "bitbucket": "\ue703",  # dev-bitbucket
}

FALLBACK_ICON = "\uf15b"  # fa-file


def entity_icon(name: str) -> str:
    """Return the Nerd Font icon for an entity (with a fallback)."""
    return ENTITY_ICONS.get(name, FALLBACK_ICON)
