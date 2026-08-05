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

DEFAULT_ICON_COLOR = "#6c7086"  # catppuccin overlay0

# A distinct Catppuccin color per entity so icons are easy to tell apart.
ENTITY_ICON_COLORS = {
    "project": "#f9e2af",  # yellow
    "compose": "#94e2d5",  # teal
    "application": "#f5c2e7",  # pink
    "postgres": "#89b4fa",  # blue
    "mysql": "#94e2d5",  # teal
    "mariadb": "#94e2d5",  # teal
    "mongo": "#a6e3a1",  # green
    "redis": "#f38ba8",  # red
    "libsql": "#89b4fa",  # blue
    "server": "#a6e3a1",  # green
    "domain": "#89dceb",  # sky
    "deployment": "#cba6f7",  # mauve
    "user": "#89b4fa",  # blue
    "notification": "#fab387",  # peach
    "backup": "#89b4fa",  # blue
    "sshKey": "#f9e2af",  # yellow
    "environment": "#f5c2e7",  # pink
    "docker": "#94e2d5",  # teal
    "registry": "#fab387",  # peach
    "tag": "#94e2d5",  # teal
    "organization": "#cba6f7",  # mauve
    "certificate": "#f9e2af",  # yellow
    "settings": "#7f849c",  # overlay1
    "port": "#a6e3a1",  # green
    "mount": "#89b4fa",  # blue
    "gitea": "#7f849c",  # overlay1
    "github": "#7f849c",  # overlay1
    "gitlab": "#7f849c",  # overlay1
    "bitbucket": "#7f849c",  # overlay1
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


# Container/docker states -> Catppuccin traffic-light color.
_STATE_COLORS = {
    "running": "#a6e3a1",  # green
    "paused": "#f9e2af",  # yellow
    "restarting": "#f9e2af",  # yellow
    "created": "#f9e2af",  # yellow
    "exited": "#f38ba8",  # red
    "dead": "#f38ba8",  # red
    "removing": "#f38ba8",  # red
    "removed": "#f38ba8",  # red
    "killed": "#f38ba8",  # red
    "stopped": "#f38ba8",  # red
}


def state_color(state: str) -> str:
    """Traffic-light color for a container state."""
    return _STATE_COLORS.get(state.lower(), DEFAULT_ICON_COLOR) if state else DEFAULT_ICON_COLOR


def state_indicator(state: str) -> str:
    """Rich markup dot (traffic light) colored by the container state."""
    return f"[bold {state_color(state)}]●[/]"
