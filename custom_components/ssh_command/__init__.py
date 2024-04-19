import logging

import voluptuous as vol

from homeassistant.core import ServiceCall
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers import config_validation as cv
from paramiko import AutoAddPolicy, RSAKey, SSHClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ssh_command'

SSH_COMMAND_SCHEMA = vol.All(
    vol.Schema({
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT): cv.string,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }, extra=vol.PREVENT_EXTRA))

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: SSH_COMMAND_SCHEMA
}, extra=vol.ALLOW_EXTRA)

def setup(hass, hass_config):
    hass.data[DOMAIN] = hass_config.get(DOMAIN, {})
    async def exec_command(call: ServiceCall):
        host = call.data.get('host', hass.data[DOMAIN].get(CONF_HOST, '172.17.0.1'))
        port = call.data.get('port', hass.data[DOMAIN].get(CONF_PORT, 22))
        username = call.data.get('user', hass.data[DOMAIN].get(CONF_USERNAME, 'pi'))
        password = call.data.get('pass', hass.data[DOMAIN].get(CONF_PASSWORD, 'raspberry'))
        command = call.data.get('command')
        ssh_private_key_path = call.data.get('ssh_private_key_path')

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())

        if ssh_private_key_path:
            try:
                key = RSAKey.from_private_key_file(ssh_private_key_path)
                client.connect(host, port, username, pkey=key)
            except Exception as e:
                _LOGGER.error(f"Failed to connect using SSH key: {e}")
                return
        else:
            # Use password for authentication if SSH key is not provided
            client.connect(host, port, username, password)

        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read()
        stderr.read()
        client.close()

        _LOGGER.info(data)

    hass.services.register(DOMAIN, 'exec_command', exec_command)

    return True


async def async_setup_entry(hass, entry):
    return True