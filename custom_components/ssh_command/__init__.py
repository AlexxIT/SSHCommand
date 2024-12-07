import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from paramiko import AutoAddPolicy, SSHClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ssh_command"

DEFAULT_SCHEMA = vol.Schema(
    {
        vol.Optional("host", default="172.17.0.1"): cv.string,
        vol.Optional("port", default=22): cv.port,
        vol.Optional("user", default="root"): cv.string,
        vol.Optional("pass"): cv.string,
        vol.Optional("private_key"): vol.Any(cv.string, cv.ensure_list),
        vol.Optional("passphrase"): cv.string,
        vol.Optional("timeout"): cv.positive_int,
    },
    extra=vol.PREVENT_EXTRA,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: DEFAULT_SCHEMA}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    default = config.get(DOMAIN) or DEFAULT_SCHEMA({})

    def exec_command(call: ServiceCall) -> dict:
        kwargs = default | call.data
        kwargs["hostname"] = kwargs.pop("host")
        kwargs["username"] = kwargs.pop("user")
        kwargs["password"] = kwargs.pop("pass", None)
        kwargs["key_filename"] = kwargs.pop("private_key", None)

        commands = kwargs.pop("command")
        if isinstance(commands, str):
            commands = [commands]

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())

        try:
            client.connect(**kwargs)

            for command in commands:
                _, stdout, stderr = client.exec_command(
                    command, timeout=kwargs.get("timeout")
                )

            # noinspection PyUnboundLocalVariable
            return {
                "stdout": stdout.read().decode("utf-8"),
                "stderr": stderr.read().decode("utf-8"),
            }

        except TimeoutError as e:
            _LOGGER.error(f"Command execution timeout")
            return {"error": repr(e)}

        except Exception as e:
            _LOGGER.error(f"Failed to connect: {repr(e)}")
            return {"error": repr(e)}

        finally:
            client.close()

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
