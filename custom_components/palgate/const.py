"""Constants for the Palgate integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "palgate"
PLATFORMS = ["cover"]

CONF_PHONE_NUMBER = "phone_number"
CONF_TOKEN_TYPE = "token_type"

CONF_ADVANCED = "advanced_options"
CONF_SECONDS_TO_OPEN = "seconds_to_open"
CONF_SECONDS_OPEN = "seconds_open"
CONF_SECONDS_TO_CLOSE = "seconds_to_close"
CONF_ALLOW_INVERT_AS_STOP = "allow_invert_as_stop"
CONF_LINK_NEW_DEVICE = "Link New Device"

SECONDS_TO_OPEN = 25
SECONDS_OPEN = 45
SECONDS_TO_CLOSE = 35
