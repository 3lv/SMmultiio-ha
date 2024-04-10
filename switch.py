import voluptuous as vol
import multiio as SMmultiio
import logging
import time

from homeassistant.const import (
	CONF_NAME
)

from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import SwitchEntity

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        NAME_PREFIX,
        SM_MAP
)
SM_SWITCH_MAP = SM_MAP["switch"]

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    type = discovery_info.get(CONF_TYPE)
    if type == "ALL":
        entities = []
        stack = discovery_info.get(CONF_STACK, 0)
        for sensor, attr in SM_SWITCH_MAP.items():
            for chan in range(int(attr["chan_no"])):
                entities.append(Switch(
                    name=NAME_PREFIX+str(stack)+"_"+sensor+"_"+str(chan+1),
                    #name=f"{NAME_PREFIX}{stack}_{sensor}_{chan+1}",
                    stack=stack,
                    type=sensor,
                    chan=str(chan+1)
                ))
        add_devices(entities)
        return
    elif type not in SM_SWITCH_MAP:
        return
    add_devices([Switch(
		name=discovery_info.get(CONF_NAME, ""),
        stack=discovery_info.get(CONF_STACK, 0),
        type=discovery_info.get(CONF_TYPE),
        chan=discovery_info.get(CONF_CHAN)
	)])

class Switch(SwitchEntity):
    """Sequent Microsystems Multiio Switch"""
    def __init__(self, name, stack, type, chan):
        if name == "":
            name = NAME_PREFIX + str(stack) + "_" + type + "_" + chan
        self._name = name
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        self._SM = SMmultiio.SMmultiio(self._stack)
        com = SM_SWITCH_MAP[self._type]["com"]
        self._SM_get = getattr(self._SM, com["get"])
        self._SM_set = getattr(self._SM, com["set"])
        self._is_on = self._SM_get(self._chan)
        self._short_timeout = .05
        self._icons = SM_SWITCH_MAP[self._type]["icon"]
        self._icon = self._icons["off"]

    def update(self):
        time.sleep(.05)
        try:
            self._is_on = self._SM_get(self._chan)
        except Exception as ex:
            _LOGGER.error(NAME_PREFIX + " %s update() failed, %e, %s, %s", self._type, ex, str(self._stack), str(self._chan))
            return
        if self._is_on:
            self._icon = self._icons["on"]
        else:
            self._icon = self._icons["off"]

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        return self._is_on

    def turn_on(self, **kwargs):
        try:
            self._SM_set(self._chan, 1)
        except Exception as ex:
            _LOGGER.error(NAME_PREFIX + " %s turn ON failed, %e", self._type, ex)

    def turn_off(self, **kwargs):
        try:
            self._SM_set(self._chan, 0)
        except Exception as ex:
            _LOGGER.error("Multiio %s turn OFF failed, %e", self._type, ex);
