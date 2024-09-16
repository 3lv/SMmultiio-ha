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

import libioplus as SMioplus

from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import generate_entity_id

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        SM_MAP, SM_API
)
SM_MAP = SM_MAP["sensor"]

#SCHEMA_EXTEND = {
#	vol.Optional(CONF_NAME, default=""): cv.string,
#	vol.Optional(CONF_STACK, default="0"): cv.string,
#}
#for key in SM_SENSOR_MAP:
#    SCHEMA_EXTEND[vol.Optional(key, default="-1")] = cv.string
#PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(SCHEMA_EXTEND)

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    add_devices([Sensor(
		name=discovery_info.get(CONF_NAME, ""),
        stack=discovery_info.get(CONF_STACK, 0),
        type=discovery_info.get(CONF_TYPE),
        chan=discovery_info.get(CONF_CHAN),
        hass=hass
	)])

class Sensor(SensorEntity):
    def __init__(self, name, stack, type, chan, hass):
        generated_name = DOMAIN + str(stack) + "_" + type + "_" + str(chan)
        self._unique_id = generate_entity_id("sensor.{}", generated_name, hass=hass)
        self._name = name or generated_name
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        # Altering class so alln functions have the same format
        self._short_timeout = .05
        self._icons = DEFAULT_ICONS | SM_MAP[self._type].get("icon", {})
        self._icon = self._icons["off"]
        self._uom = SM_MAP[self._type]["uom"]
        self._value = 0
        self.__SM__init()

        # Custom setup
        # I Don't like this hardcoded setup, maybe add a setup com in data.py
        if self._type == "opto_cnt":
            self._SM.rstOptoCount(self._stack, self._chan)
            ## THIS DOESN"T WORK IDK WHY
            res = self._SM.cfgOptoEdgeCount(self._stack, self._chan, 1)
            _LOGGER.error(res) # res is 1, so it SHOULD be working
        ## END

    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_get = getattr(self._SM, com["get"])
        else:
            def _aux_SM_get(*args):
                return getattr(self._SM, com["get"])(self._stack, *args)
            self._SM_get = _aux_SM_get

    def update(self):
        if self._type == "opto_cnt":
            time.sleep(self._short_timeout)
            ## IT DOESN"T WORK WITHOUT THIS IDK WHY
            self._SM.cfgOptoEdgeCount(self._stack, self._chan, 1)
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
    def native_value(self):
        return self._value
