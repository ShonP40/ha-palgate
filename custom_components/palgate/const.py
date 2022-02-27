"""Constants for the Palgate integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "palgate"
PLATFORMS = ["cover"]

SECONDS_TO_OPEN = 25
SECONDS_OPEN = 45
SECONDS_TO_CLOSE = 35
