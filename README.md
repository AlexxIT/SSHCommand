# SSHCommand for Home Assistant

Run any SSH command on remote server from [Home Assistant](https://www.home-assistant.io/) service call. For example, the command on the main host from the docker container.

## Installation

[HACS](https://hacs.xyz/) custom repository: `AlexxIT/SSHCommand`.

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=AlexxIT&repository=SSHCommand&category=Integration)

Or manually copy `ssh_command` folder from [latest release](https://github.com/AlexxIT/SSHCommand/releases/latest) to `/config/custom_components` folder.

## Configuration

Add integration via Home Assistant UI or `configuration.yaml`.

[![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ssh_command)

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
        timeout: 5
```

If you want connect with ssh key, use this:

```yaml
script:
  run_on_host:
    alias: Run shell command on host
    sequence:
    - service: ssh_command.exec_command
      data:
        host: 192.168.1.123
        user: pi
        private_key: /config/ssh/id_rsa
        command: ls -la
        timeout: 5
```

If you want use secrets or change default values, add them to `configuration.yaml`:

```yaml
ssh_command:
  host: 192.168.1.123
  port: 22
  user: pi
  pass: !secret ssh_parssword
  timeout: 5
```
