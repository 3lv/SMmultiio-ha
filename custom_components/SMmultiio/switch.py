DEFAULT_ICONS = {
        "on": "mdi:toggle-switch-variant",
        "off": "mdi:toggle-switch-variant-off",
}

import logging
import time
import types
import inspect
from inspect import signature

from homeassistant.const import (
	CONF_NAME
)

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import generate_entity_id

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        SM_MAP, SM_API
)
SM_MAP = SM_MAP["switch"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    # TODO CHECK IF ALREADY CONFIGURED FOR WHATEVER REASON
    add_devices([Switch(
		name=discovery_info.get(CONF_NAME, ""),
        stack=discovery_info.get(CONF_STACK, 0),
        type=discovery_info.get(CONF_TYPE),
        chan=discovery_info.get(CONF_CHAN),
        hass=hass,
	)])

class Switch(SwitchEntity):
    """Sequent Microsystems HomeAutomation Switch"""
    def __init__(self, name, stack, type, chan, hass):
        generated_name = DOMAIN + str(stack) + "_" + type + "_" + str(chan)
        self._unique_id = generate_entity_id("switch.{}", generated_name, hass=hass)
        self._name = name or generated_name
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        self._short_timeout = .05
        self._icons = DEFAULT_ICONS | SM_MAP[self._type].get("icon", {})
        self._icon = self._icons["off"]
        self.__SM__init()
        self._is_on = self._SM_get(self._chan)

    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_get = getattr(self._SM, com["get"])
            self._SM_set = getattr(self._SM, com["set"])
            ### Make API compatible if channel is not used (_)
            if len(signature(self._SM_get).parameters) == 0:
                def _aux2_SM_get(self, _):
                    return getattr(self, com["get"])()
                self._SM_get = types.MethodType(_aux2_SM_get, self._SM)
            if len(signature(self._SM_set).parameters) == 1:
                def _aux2_SM_set(self, _, value):
                    getattr(self, com["set"])(value)
                self._SM_set = types.MethodType(_aux2_SM_set, self._SM)
        else:
            _SM_get = getattr(self._SM, com["get"])
            if len(signature(_SM_get).parameters) == 1:
                def _aux3_SM_get(_, *args):
                    return _SM_get(self._stack, *args)
                self._SM_get = _aux3_SM_get
            else:
                def _aux_SM_get(*args):
                    return _SM_get(self._stack, *args)
                self._SM_get = _aux_SM_get
            _SM_set = getattr(self._SM, com["set"])
            if len(signature(_SM_set).parameters) == 2:
                def _aux3_SM_set(_, *args):
                    return _SM_set(self._stack, *args)
                self._SM_set = _aux3_SM_set
            else:
                def _aux_SM_set(*args):
                    return _SM_set(self._stack, *args)
                self._SM_set = _aux_SM_set

    def update(self):
        time.sleep(self._short_timeout)
        try:
            self._is_on = self._SM_get(self._chan)
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s update() failed, %e, %s, %s", self._type, ex, str(self._stack), str(self._chan))
            return
        if self._is_on:
            self._icon = self._icons["on"]
        else:
            self._icon = self._icons["off"]

    @property
    def unique_id(self):
        return self._unique_id

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
            _LOGGER.error(DOMAIN + " %s turn ON failed, %e", self._type, ex)

    def turn_off(self, **kwargs):
        try:
            self._SM_set(self._chan, 0)
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s turn OFF failed, %e", self._type, ex);
