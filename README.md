# Dokli

A magical CLI/TUI for interacting with [Dokploy](https://github.com/Dokploy/dokploy).

## Installation

```bash
pip install git+https://github.com/jonykalavera/dokli.git
```

Tested with Dokploy versions:

- 0.6.1

## Configuration

Create a dokly.yaml file in the current directory. Example:

```yaml
connections:
  - name: test-env
    url: https://dokploy.examle.com
    api_key: ****************************************
    notes: "Our test environment. Handle with care!"
```

## CLI

### Features

- Supports all API entities actions/verbs.
- magical JSON parameters `%json:{"projectId": "daspdoada798sda"}`
- magical file parameters `%file:foo.redis.json`
- output formats:
  - yaml
  - json
  - python
  - table (experimental)

## Usage

```bash
$ dokly --help

 Usage: dokli [OPTIONS] COMMAND [ARGS]...

 Magical Dokploy CLI/TUI.
 No commands, launches the TUI.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ api   API.                                                                   │
╰──────────────────────────────────────────────────────────────────────────────╯


$ dokly api test-env project all
- adminId: ysHDHlhX4a3zOG2fLsske
  applications: []
  compose: []
  createdAt: '2024-08-05T02:45:38.168Z'
  description: null
  mariadb: []
  mongo: []
  mysql: []
  name: Dokli
  postgres: []
  projectId: zuanf1SWHMFO11y6xqpRR
  redis: []

$ dokli api test-env project create -p '%json:{"name": "Dokli"}' --format table
               API Response
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key         ┃ Value                    ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ projectId   │ zuanf1SWHMFO11y6xqpRR
│ name        │ Dokli                    │
│ description │ None                     │
│ createdAt   │ 2024-08-05T02:45:38.168Z │
│ adminId     │ ysHDHlhX4a3zOG2fLsske    │
└─────────────┴──────────────────────────┘

$ dokli api test-env project one --format json -p project_id=zuanf1SWHMFO11y6xqpRR
{"projectId": "zuanf1SWHMFO11y6xqpRR", "name": "Dokli", "description": null,
"createdAt": "2024-08-05T02:45:38.168Z", "adminId": "ysHDHlhX4a3zOG2fLsske",
"applications": [], "mariadb": [], "mongo": [], "mysql": [], "postgres": [],
"redis": [], "compose": []}
```

### Known issues

- Configuration stores API key in plain-text.
- No way to hide secrets. Passwords are printed in plain-text.

## TUI

Still a WIP.

[![Dokli TUI initial development](http://img.youtube.com/vi/IAnHfFV9_jU/0.jpg)](http://www.youtube.com/watch?v=IAnHfFV9_jU "Dokli TUI initial development")

## Buy me a taco

I'm Mexican, I prefer tacos. But coffee is also nice. You can use the sponsor button on the top. Also pretty please and thanks in advance 🥺.



