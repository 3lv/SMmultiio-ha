DEFAULT_ICONS = {
        "on": "mdi:numeric",
        "off": "mdi:numeric-0",
}

import logging
import time
import types
import inspect
from inspect import signature
_LOGGER = logging.getLogger(__name__)

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import generate_entity_id

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        COM_NOGET,
        SM_MAP, SM_API
)
SM_MAP = SM_MAP["number"]

async def async_setup_platform(hass, config, add_devices, discovery_info=None):
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
        self._uom = SM_MAP[self._type].get("uom", "")
        self._min_value = SM_MAP[self._type]["min_value"]
        self._max_value = SM_MAP[self._type]["max_value"]
        self._step = SM_MAP[self._type]["step"]
        self._value = 0
        self.__SM__init()

    ### Make API compatible if channel is not used or if it requires integer value
    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_get = getattr(self._SM, com["get"])
            self._SM_set = getattr(self._SM, com["set"])
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
                def _aux3_SM_get(_):
                    return _SM_get(self._stack)
                self._SM_get = _aux3_SM_get
            else:
                def _aux_SM_get(chan):
                    return _SM_get(self._stack, chan)
                self._SM_get = _aux_SM_get
            _SM_set = getattr(self._SM, com["set"])
            if self._step == int(self._step):
                if len(signature(_SM_set).parameters) == 2:
                    def _aux3_SM_set(_, value):
                        return _SM_set(self._stack, int(value))
                    self._SM_set = _aux3_SM_set
                else:
                    def _aux_SM_set(chan, value):
                        return _SM_set(self._stack, chan, int(value))
                    self._SM_set = _aux_SM_set
            else:
                if len(signature(_SM_set).parameters) == 2:
                    def _aux3_SM_set(_, value):
                        return _SM_set(self._stack, value)
                    self._SM_set = _aux3_SM_set
                else:
                    def _aux_SM_set(chan, value):
                        return _SM_set(self._stack, chan, value)
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
    ## TODO implement
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
