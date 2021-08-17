# SSHCommand for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This [Home Assistant](https://www.home-assistant.io/) service allows you to run SSH commands on remote host. Example main host from Docker container with Hass.

## Installation

**Method 1.** [HACS](https://hacs.xyz/) custom repo:

> HACS > Integrations > 3 dots (upper top corner) > Custom repositories > URL: `AlexxIT/SSHCommand`, Category: Integration > Add > wait > SSHCommand > Install

**Method 2.** Manually copy `ssh_command` folder from [latest release](https://github.com/AlexxIT/SSHCommand/releases/latest) to `/config/custom_components` folder.

## Configuration

**Method 1.** GUI:

> Configuration > Integrations > Add Integration > **SSHCommand**

If the integration is not in the list, you need to clear the browser cache.

**Method 2.** YAML:

```yaml
ssh_command:
  host: 192.168.1.123 # Optional
  port: 22 # Optional
  username: pi # Optional
  password: raspberry # Optional
```

## Usage

New service `ssh_command.exec_command`:

```yaml
script:
  run_on_host:
    alias: Run shell command on host
    sequence:
    - service: ssh_command.exec_command
      data:
        host: 192.168.1.123
        port: 22
        user: pi
        pass: raspberry
        command: ls -la
```