# Dokli

A magical CLI/TUI for interacting with [Dokploy](https://github.com/Dokploy/dokploy).

```txt
                                                                    █
                                                                   ████
                                                                    ███████            █
               █████████████████████████                             ████████   ████████
             ███████████████████████████████                          ██████████████████
            ████                        █████████                       ██████████████
            ████          ███               █████████                      ████
            ███           ███                   ██████████               █████
            ███                                      ████████████████████████
            ████████████████                              █████████████████
            ██████████████████████                               ███████
            ████            ██████████                     ██████████          ██████
             ██████               ███████████████████████████████          ████████
               ████████                ████████████████████             ████████
             █     █████████                                        ████████     ███
            █████      █████████                                ████████      ██████
            ████████       ███████████                    ███████████      █████████
            ████ ██████         ████████████████████████████████        ███████ ████
            ████   ███████            ████████████████████           ███████    ████
             █████    ████████                                   ████████    ██████
              ███████     ████████                           █████████     ███████
              █████████      ████████████              ███████████      ██████████
               ████ ██████        ████████████████████████████       ███████ ████
                ████   ██████            ██████████████            ██████   ████
                 █████   ███████                               ████████   █████
                   █████    █████████                      █████████    █████
                    ██████      ████████████████████████████████      ██████
                      ██████         ██████████████████████         ██████
                        ███████                                  ██████
                           ████████                          ████████
                              ███████████               ██████████
                                   ██████████████████████████
                                          ████████████
```

## Installation

```bash
pip install git+https://github.com/jonykalavera/dokli.git
# with TUI support
pip install git+https://github.com/jonykalavera/dokli.git#egg=dokli[tui]
```

Tested with Dokploy versions:

- 0.6.1
- 0.18.1

## Configuration

Create the configuration file at `~/.config/dokli/dokli.yaml`. Example:

```yaml
connections:
  - name: test-env
    url: https://test.examle.com
    api_key: ****************************************
    notes: "Our test environment. Handle with care!"
  - name: prod-env
    url: https://prod.examle.com
    api_key: ****************************************
    notes: "Our prod environment. Handle with care!"
```

## CLI

### Features

- Commands are inferred from the OpenAPI spec, which allows:
  - support for multiple Dokploy API versions.
  - support for all API entities actions/verbs.
- magical JSON parameters `%json:{"projectId": "daspdoada798sda"}`
- magical file parameters `%file:/path/to/data/foo.redis.json`
- output formats:
  - yaml
  - json
  - python
  - table (experimental)

## Usage

```bash
$ dokly


 Usage: python -m dokli [OPTIONS] COMMAND [ARGS]...

 Magical Dokploy CLI/TUI.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ test-env   Dokploy Instance: https://test.examle.com.                        │
│ prod-env   Dokploy Instance: https://prod.examle.com.                        │
│ tui        Text User Interface.                                              │
╰──────────────────────────────────────────────────────────────────────────────╯


$ dokly test-env project all
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

$ dokli test-env project create --body '%json:{"name": "Dokli"}' --format table
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

$ dokli test-env project one --format json zuanf1SWHMFO11y6xqpRR
{"projectId": "zuanf1SWHMFO11y6xqpRR", "name": "Dokli", "description": null,
"createdAt": "2024-08-05T02:45:38.168Z", "adminId": "ysHDHlhX4a3zOG2fLsske",
"applications": [], "mariadb": [], "mongo": [], "mysql": [], "postgres": [],
"redis": [], "compose": []}
```

## TUI

Still a WIP.
![Screenshot from 2024-08-04 23-39-14](https://github.com/user-attachments/assets/9943d053-f3a6-40dd-90b7-07502fb81925)
![Screenshot from 2024-08-04 23-39-04](https://github.com/user-attachments/assets/acce2413-7b48-472d-899a-71d469b6113d)
![Screenshot from 2024-08-05 00-06-58](https://github.com/user-attachments/assets/17fefe01-e072-4c18-8cc1-159de9e94adc)

[http://www.youtube.com/watch?v=IAnHfFV9_jU](http://www.youtube.com/watch?v=IAnHfFV9_jU)

## Motivation

The CLI is designed to keep up with any changes in the API. Commands are dynamically inferred from the OpenAPI spec.
I did this because I want to do some test automation and the official CLI seems incomplete at the moment. The TUI is because I am into tools like [yazi](https://yazi-rs.github.io/), [lazygit](https://github.com/jesseduffield/lazygit), [k9s](https://k9scli.io/), [dry](https://github.com/moncho/dry), etc. I like to keep my terminal open at all times `$`.
Also, it seemed to me like something cool to do this weekend. I learned a bunch about [texual](https://textual.textualize.io/), [typer](https://github.com/tiangolo/typer) and [Dokploy](https://github.com/Dokploy/dokploy).

## Buy me a 🌮

I'm Mexican, I prefer tacos. But ☕ is also nice. You can use the 🫶 sponsor button on the top.

Also pretty please and thanks in advance 🥺.
