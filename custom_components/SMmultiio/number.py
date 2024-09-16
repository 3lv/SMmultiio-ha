DEFAULT_ICONS = {
        "on": "mdi:numeric",
        "off": "mdi:numeric-0",
}

import voluptuous as vol
import logging
import time
import types
import inspect
from inspect import signature
_LOGGER = logging.getLogger(__name__)

import libioplus as SMioplus

from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import generate_entity_id

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        COM_NOGET,
        SM_MAP, SM_API
)
SM_MAP = SM_MAP["number"]

def setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    type=discovery_info.get(CONF_TYPE)
    if SM_MAP[type]["com"]["get"] == COM_NOGET:
        add_devices([Number_NOGET(
            name=discovery_info.get(CONF_NAME, ""),
            stack=discovery_info.get(CONF_STACK, 0),
            type=discovery_info.get(CONF_TYPE),
            chan=discovery_info.get(CONF_CHAN),
            hass=hass
        )])
    else:
        add_devices([Number(
            name=discovery_info.get(CONF_NAME, ""),
            stack=discovery_info.get(CONF_STACK, 0),
            type=discovery_info.get(CONF_TYPE),
            chan=discovery_info.get(CONF_CHAN),
            hass=hass
        )])

class Number(NumberEntity):
    """Sequent Microsystems Multiio Switch"""
    def __init__(self, name, stack, type, chan, hass):
        generated_name = DOMAIN + str(stack) + "_" + type + "_" + str(chan)
        self._unique_id = generate_entity_id("number.{}", generated_name, hass=hass)
        self._name = name or generated_name
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        self._short_timeout = .05
        self._icons = DEFAULT_ICONS | SM_MAP[self._type].get("icon", {})
        self._icon = self._icons["off"]
        self._uom = SM_MAP[self._type]["uom"]
        self._min_value = SM_MAP[self._type]["min_value"]
        self._max_value = SM_MAP[self._type]["max_value"]
        self._step = SM_MAP[self._type]["step"]
        self._value = 0
        self.__SM__init()

    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_get = getattr(self._SM, com["get"])
            self._SM_set = getattr(self._SM, com["set"])
        else:
            def _aux_SM_get(*args):
                return getattr(self._SM, com["get"])(self._stack, *args)
            self._SM_get = _aux_SM_get
            def _aux_SM_set(*args):
                return getattr(self._SM, com["set"])(self._stack, *args)
            self._SM_set = _aux_SM_set

    def update(self):
        time.sleep(self._short_timeout)
        try:
            self._value = self._SM_get(self._chan)
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s update() failed, %e, %s, %s", self._type, ex, str(self._stack), str(self._chan))
            return
        if self._value != 0:
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
    def native_unit_of_measurement(self):
        return self._uom

    @property
    def native_step(self):
        return self._step

    @property
    def native_min_value(self):
        return self._min_value

    @property
    def native_max_value(self):
        return self._max_value

    @property
    def native_value(self):
        return self._value

    def set_native_value(self, value):
        try:
            self._SM_set(self._chan, value)
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s setting value failed, %e", self._type, ex)

## Lazy class, uses the set value as the get value
class Number_NOGET(Number):
    ## TODO
    def update(self):
        time.sleep(self._short_timeout)
        if self._value != 0:
            self._icon = self._icons["on"]
        else:
            self._icon = self._icons["off"]

    def set_native_value(self, value):
        try:
            self._SM_set(self._chan, value)
            self._value = value
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s setting value failed, %e", self._type, ex)

    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_set = getattr(self._SM, com["set"])
        else:
            def _aux_SM_set(*args):
                return getattr(self._SM, com["set"])(self._stack, *args)
            self._SM_set = _aux_SM_set
