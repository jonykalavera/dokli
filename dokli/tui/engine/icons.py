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

DEFAULT_ICON_COLOR = "grey70"

# A distinct color per entity so icons are easy to tell apart.
ENTITY_ICON_COLORS = {
    "project": "yellow",
    "compose": "cyan",
    "application": "magenta",
    "postgres": "blue",
    "mysql": "cyan",
    "mariadb": "cyan",
    "mongo": "green",
    "redis": "red",
    "libsql": "blue",
    "server": "green",
    "domain": "blue",
    "deployment": "magenta",
    "user": "blue",
    "notification": "yellow",
    "backup": "blue",
    "sshKey": "yellow",
    "environment": "magenta",
    "docker": "cyan",
    "registry": "yellow",
    "tag": "cyan",
    "organization": "magenta",
    "certificate": "yellow",
    "settings": "grey",
    "port": "green",
    "mount": "blue",
    "gitea": "grey",
    "github": "grey",
    "gitlab": "grey",
    "bitbucket": "grey",
}


def entity_icon(name: str) -> str:
    """Return the Nerd Font icon for an entity (with a fallback)."""
    return ENTITY_ICONS.get(name, FALLBACK_ICON)


def entity_icon_color(name: str) -> str:
    """Return the color for an entity's icon."""
    return ENTITY_ICON_COLORS.get(name, DEFAULT_ICON_COLOR)


def icon_label(name: str) -> str:
    """Rich markup for an entity icon inside a colored box."""
    return f"[b on {entity_icon_color(name)}] {entity_icon(name)} [/]"
