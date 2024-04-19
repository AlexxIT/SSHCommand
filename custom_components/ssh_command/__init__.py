import logging

import voluptuous as vol
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from paramiko import AutoAddPolicy, RSAKey, SSHClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ssh_command"

SSH_COMMAND_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Optional(CONF_HOST): cv.string,
            vol.Optional(CONF_PORT): cv.string,
            vol.Optional(CONF_USERNAME): cv.string,
            vol.Optional(CONF_PASSWORD): cv.string,
            vol.Optional("private_key"): cv.string,
        },
        extra=vol.PREVENT_EXTRA,
    )
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: SSH_COMMAND_SCHEMA}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    config: dict = config.get(DOMAIN) or {}

    def exec_command(call: ServiceCall):
        host = call.data.get("host", config.get(CONF_HOST, "172.17.0.1"))
        port = call.data.get("port", config.get(CONF_PORT, 22))
        username = call.data.get("user", config.get(CONF_USERNAME, "pi"))
        password = call.data.get("pass", config.get(CONF_PASSWORD, "raspberry"))
        command = call.data.get("command")

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())

        try:
            if private_key := call.data.get("private_key"):
                key = RSAKey.from_private_key_file(private_key)
                client.connect(host, port, username, pkey=key)
            else:
                # Use password for authentication if SSH key is not provided
                client.connect(host, port, username, password)
        except Exception as e:
            _LOGGER.error(f"Failed to connect: {repr(e)}")
            return {"error": repr(e)}

        _, stdout, stderr = client.exec_command(command)
        response = {
            "command": command,
            "stdout": stdout.read().decode("utf-8"),
            "stderr": stderr.read().decode("utf-8"),
        }
        client.close()

        _LOGGER.info(response)

    # ServiceResponse from Hass 2023.7
    # https://github.com/home-assistant/core/blob/2023.7.0/homeassistant/core.py
    hass.services.async_register(
        DOMAIN, "exec_command", exec_command, SSH_COMMAND_SCHEMA
    )

    return True


async def async_setup_entry(hass, entry):
    return True
