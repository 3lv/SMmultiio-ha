import voluptuous as vol
import logging
import time
import types
import inspect
from inspect import signature
_LOGGER = logging.getLogger(__name__)

import multiio as SMmultiio

from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.number import NumberEntity

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        NAME_PREFIX,
        SM_MAP
)
SM_NUMBER_MAP = SM_MAP["number"]

def setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    type = discovery_info.get(CONF_TYPE)
    if type == "ALL":
        entities = []
        stack=discovery_info.get(CONF_STACK, 0)
        for sensor, attr in SM_NUMBER_MAP.items():
            for chan in range(int(attr["chan_no"])):
                entities.append(Number(
                    name=NAME_PREFIX+str(stack)+"_"+sensor+"_"+str(chan+1),
                    stack=stack,
                    type=sensor,
                    chan=str(chan+1)
                ))
        add_devices(entities)
        return
    elif type not in SM_NUMBER_MAP:
        return
    add_devices([Number(
		name=discovery_info.get(CONF_NAME, ""),
        stack=discovery_info.get(CONF_STACK, 0),
        type=discovery_info.get(CONF_TYPE),
        chan=discovery_info.get(CONF_CHAN)
	)])

class Number(NumberEntity):
    """Sequent Microsystems Multiio Switch"""
    def __init__(self, name, stack, type, chan):
        if name == "":
            name = NAME_PREFIX + str(stack) + "_" + type + "_" + chan
        self._name = name
        _LOGGER.error("%s", stack)
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        self._SM = SMmultiio.SMmultiio(self._stack)
        # Altering class so all functions have the same format
        com = SM_NUMBER_MAP[self._type]["com"]
        self._short_timeout = .05
        self._icons = SM_NUMBER_MAP[self._type]["icon"]
        self._icon = self._icons["off"]
        self._uom = SM_NUMBER_MAP[self._type]["uom"]
        self._min_value = SM_NUMBER_MAP[self._type]["min_value"]
        self._max_value = SM_NUMBER_MAP[self._type]["max_value"]
        self._step = SM_NUMBER_MAP[self._type]["step"]
        self._value = 0
        self._SM_get = getattr(self._SM, com["get"])
        if len(signature(self._SM_get).parameters) == 0:
            def _aux_SM_get(self, _):
                return getattr(self, com["get"])()
            self._SM_get = types.MethodType(_aux_SM_get, self._SM)
        self._SM_set = getattr(self._SM, com["set"])
        if len(signature(self._SM_set).parameters) == 1:
            def _aux_SM_set(self, _, value):
                getattr(self, com["set"])(value)
            self._SM_set = types.MethodType(_aux_SM_set, self._SM)

    def update(self):
        time.sleep(self._short_timeout)
        try:
            self._value = self._SM_get(self._chan)
        except Exception as ex:
            _LOGGER.error(NAME_PREFIX + " %s update() failed, %e, %s, %s", self._type, ex, str(self._stack), str(self._chan))
            return
        if self._value != 0:
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
            _LOGGER.error(NAME_PREFIX + " %s setting value failed, %e", self._type, ex)
