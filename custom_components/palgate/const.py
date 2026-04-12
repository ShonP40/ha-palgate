"""Constants for the Palgate integration."""

from datetime import timedelta
DOMAIN = "palgate"
PLATFORMS = ["cover", "select"]

CONF_PHONE_NUMBER = "phone_number"
CONF_TOKEN_TYPE = "token_type"

CONF_ADVANCED = "advanced_options"
CONF_SECONDS_TO_OPEN = "seconds_to_open"
CONF_SECONDS_OPEN = "seconds_open"
CONF_SECONDS_TO_CLOSE = "seconds_to_close"
CONF_ALLOW_INVERT_AS_STOP = "allow_invert_as_stop"
CONF_LINK_NEW_DEVICE = "Link New Device"

GATE_MODE_NORMAL      = "normal"
GATE_MODE_HOLD_OPEN   = "hold_open"
GATE_MODE_HOLD_CLOSED = "hold_closed"

SECONDS_TO_OPEN = 25
SECONDS_OPEN = 45
SECONDS_TO_CLOSE = 35

# Polling interval, applicable to SELECT platform only (disabled by default)
SCAN_INTERVAL = timedelta(minutes=1)
