# SSHCommand

```yaml
ssh_command:

script:
  run_on_host:
    alias: Run shell command on host
    sequence:
    - service: ssh_command.exec_command
      data:
        host: 192.168.1.123
        user: pi
        pass: raspberry
        command: ls -la
```