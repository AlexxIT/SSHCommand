from homeassistant.const import REQUIRED_PYTHON_VER

from custom_components.ssh_command import *
from custom_components.ssh_command.config_flow import *


def test_backward():
    # https://github.com/home-assistant/core/blob/2023.2.0/homeassistant/const.py
    assert REQUIRED_PYTHON_VER >= (3, 10, 0)

    assert async_setup_entry
    assert ConfigFlowHandler
