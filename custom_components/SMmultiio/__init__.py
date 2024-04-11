"""Sequent Microsystems Multiio Integration"""

import logging
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
	CONF_NAME
)
CONF_NAME = CONF_NAME
CONF_STACK = "stack"
CONF_TYPE = "type"
CONF_CHAN = "chan"

"""
SMmultiio:
    -   stack: 0
        rtd_res-1:
            #optional
            name: super
        rtd_temp-1:
"""

DOMAIN = "SMmultiio"
NAME_PREFIX = "SMmultiio"
SM_MAP = {
    "sensor":  {
        "rtd_res": {
                "chan_no": 2,
                "uom": "Ohm",
                "com": {
                    "get": "get_rtd_res",
                },
                "icon": {
                    "on": "mdi:flash-triangle",
                    "off": "mdi:flash-triangle"
                },
                "optional": True
        },
        "rtd_temp": {
                "chan_no": 2,
                "uom": "°C",
                "com": {
                    "get": "get_rtd_temp",
                },
                "icon": {
                    "on": "mdi:flash-triangle",
                    "off": "mdi:flash-triangle"
                }
        },
        "iin": {
                "chan_no": 2,
                "uom": "mA",
                "com": {
                    "get": "get_i_in",
                },
                "icon": {
                    "on": "mdi:flash-triangle",
                    "off": "mdi:flash-triangle"
                }
        },
        "uin": {
                "chan_no": 2,
                "uom": "V",
                "com": {
                    "get": "get_i_in",
                },
                "icon": {
                    "on": "mdi:flash-triangle",
                    "off": "mdi:flash-triangle"
                }
        },
    },
    "switch": {
        "led": {
                "chan_no": 6,
                "com": {
                    "get": "get_led",
                    "set": "set_led"
                },
                "icon": {
                    "on": "mdi:led-on",
                    "off": "mdi:led-off"
                }
        },
        "relay": {
                "chan_no": 2,
                "com": {
                    "get": "get_relay",
                    "set": "set_relay"
                },
                "icon": {
                    "on": "mdi:toggle-switch-variant",
                    "off": "mdi:toggle-switch-variant-off",
                }
        }
    },
    "number": {
        "uout": {
                "chan_no": 2,
                "uom": "V",
                "min_value": 0.0,
                "max_value": 10.0,
                "step": 0.01,
                "com": {
                    "get": "get_u_out",
                    "set": "set_u_out"
                },
                "icon": {
                    "on": "mdi:flash-triangle",
                    "off": "mdi:flash-triangle"
                }
        },
        "iout": {
                "chan_no": 2,
                "uom": "mA",
                "min_value": 4.0,
                "max_value": 20.0,
                "step": 0.01,
                "com": {
                    "get": "get_i_out",
                    "set": "set_i_out"
                },
                "icon": {
                    "on": "mdi:current-dc",
                    "off": "mdi:current-dc"
                }
        },
        "servo": {
                "chan_no": 2,
                "uom": "%",
                "min_value": -140.0,
                "max_value": +140.0,
                "step": 0.1,
                "com": {
                    "get": "get_servo",
                    "set": "set_servo"
                },
                "icon": {
                    "on": "mdi:vector-triangle",
                    "off": "mdi:vector-triangle"
                }
        },
        "motor": {
                "chan_no": 1,
                "uom": "%",
                "min_value": -100.0,
                "max_value": +100.0,
                "step": 0.1,
                "com": {
                    "get": "get_motor",
                    "set": "set_motor"
                },
                "icon": {
                    "on": "mdi:vector-triangle",
                    "off": "mdi:vector-triangle"
                }
        },
}
}


CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema(vol.Any([vol.Schema({
        vol.Optional(CONF_STACK, default="0"): cv.string,
    }, extra=vol.ALLOW_EXTRA)], {}))
}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

def load_platform(hass, entity_config):
        for platform_type, attr in SM_MAP.items():
            if entity_config[CONF_TYPE] in attr:
                hass.helpers.discovery.load_platform(
                        platform_type, DOMAIN, entity_config, entity_config
                )
def load_all_platforms(hass, stack=0):
    for platform_type, platform in SM_MAP.items():
        for type, attr in platform.items():
            if attr.get("optional", False):
                continue
            for chan in range(int(attr["chan_no"])):
                entity_config = {
                        CONF_NAME: NAME_PREFIX+str(stack)+"_"+type+"_"+str(chan+1),
                        CONF_STACK: stack,
                        CONF_TYPE: type,
                        CONF_CHAN: chan+1
                }
                hass.helpers.discovery.load_platform(
                        platform_type, DOMAIN, entity_config, {}
                )


def setup(hass, config):
    hass.data[DOMAIN] = []
    card_configs = config.get(DOMAIN)
    if not card_configs:
        load_all_platforms(hass, stack=0)
        return True
    for card_config in card_configs:
        stack = int(card_config.pop(CONF_STACK, 0))
        if not card_config:
            load_all_platforms(hass, stack=stack)
            continue
        for entity in card_config:
            try:
                [type, chan] = entity.rsplit("_", 1)
                chan = int(chan)
            except:
                _LOGGER.error(entity, " doesn't respect type-chan format")
                continue
            entity_config = card_config[entity] or {}
            entity_config |= {
                    CONF_NAME: NAME_PREFIX + str(stack) + "_" + entity,
                    CONF_STACK: stack,
                    CONF_TYPE: type,
                    CONF_CHAN: chan
            }
            load_platform(hass, entity_config)
        
    return True
