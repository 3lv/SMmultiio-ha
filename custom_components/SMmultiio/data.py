"""Sequent Microsystems Multiio Integration"""

import multiio
API = multiio.SMmultiio
DOMAIN = "SMmultiio"
NAME_PREFIX = "mio"

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
