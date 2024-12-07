import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from paramiko import AutoAddPolicy, RSAKey, SSHClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ssh_command"

DEFAULT_SCHEMA = vol.Schema(
    {
        vol.Optional("host", default="172.17.0.1"): cv.string,
        vol.Optional("port", default=22): cv.port,
        vol.Optional("user", default="pi"): cv.string,
        vol.Optional("pass", default="raspberry"): cv.string,
        vol.Optional("timeout", default=5): cv.positive_int,
    },
    extra=vol.PREVENT_EXTRA,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: DEFAULT_SCHEMA}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    default = config[DOMAIN] if DOMAIN in config else DEFAULT_SCHEMA({})

    def exec_command(call: ServiceCall) -> dict:
        host = call.data.get("host", default["host"])
        port = call.data.get("port", default["port"])
        username = call.data.get("user", default["user"])
        password = call.data.get("pass", default["pass"])
        timeout = call.data.get("timeout", default["timeout"])
        command = call.data["command"]

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())

        try:
            if private_key := call.data.get("private_key"):
                key = RSAKey.from_private_key_file(private_key)
                client.connect(host, port, username, pkey=key, timeout=timeout)
            else:
                # Use password for authentication if SSH key is not provided
                client.connect(host, port, username, password, timeout=timeout)
        except Exception as e:
            _LOGGER.error(f"Failed to connect: {repr(e)}")
            return {"error": repr(e)}

        try:
            _, stdout, stderr = client.exec_command(command, timeout=timeout)
        except TimeoutError as e:
            _LOGGER.error(f"Command execution timeout")
            return {"error": repr(e)}

        response = {
            "command": command,
            "stdout": stdout.read().decode("utf-8"),
            "stderr": stderr.read().decode("utf-8"),
        }
        client.close()

        _LOGGER.debug(response)

        return response

    try:
        # ServiceResponse from Hass 2023.7
        # https://github.com/home-assistant/core/blob/2023.7.0/homeassistant/core.py
        from homeassistant.core import SupportsResponse

        hass.services.async_register(
            DOMAIN,
            "exec_command",
            exec_command,
            supports_response=SupportsResponse.OPTIONAL,
        )
    except ImportError:
        hass.services.async_register(DOMAIN, "exec_command", exec_command)

    return True


async def async_setup_entry(hass, entry):
    return True
