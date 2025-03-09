"""The Palgate integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN as PALGATE_DOMAIN
from .const import *


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Palgate from a config entry."""


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):

    if config_entry.version > 3:
        return False

    new_data = dict(config_entry.data)

    if config_entry.version < 2:

        new_data[CONF_TOKEN_TYPE] = "1"

    if config_entry.version < 3:

        new_data[CONF_ADVANCED] = {
            CONF_SECONDS_TO_OPEN : SECONDS_TO_OPEN,
            CONF_SECONDS_OPEN : SECONDS_OPEN,
            CONF_SECONDS_TO_CLOSE : SECONDS_TO_CLOSE,
            CONF_ALLOW_INVERT_AS_STOP : False
        }

    hass.config_entries.async_update_entry(config_entry, data=new_data, version=3)

    return True
