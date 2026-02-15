"""The Palgate integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers import device_registry as dr, entity_registry as er
import logging

from .const import DOMAIN as PALGATE_DOMAIN
from .const import *

_LOGGER: logging.Logger = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Palgate from a config entry."""


    _LOGGER.debug(f"Setting up Palgate config entry: {entry.entry_id}, device_id: {entry.data[CONF_DEVICE_ID]}")
    # Register a unique device for this gate
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(PALGATE_DOMAIN, entry.data[CONF_DEVICE_ID])},
        name=entry.title,
        manufacturer="Palgate",
        model="Gate Controller",
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Try to cleanup orphaned legacy multi-gate device (idempotent, safe to call multiple times)
    await _cleanup_orphaned_device(hass)
    
    return True

async def _cleanup_orphaned_device(hass: HomeAssistant) -> None:
    """Remove the old shared 'Palgate' device if it's orphaned."""

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    
    _LOGGER.debug("Checking for orphaned legacy 'palgate' device...")
    
    # Find the old shared device with the exact legacy identifier
    old_device = device_registry.async_get_device(
        identifiers={(PALGATE_DOMAIN, "palgate")}
    )
    
    if not old_device:
        _LOGGER.debug("No legacy 'palgate' device found")
        return
    
    _LOGGER.debug(f"Found legacy (multi-gate) device: {old_device.id}, config_entries: {old_device.config_entries}")
    
    # Check if it has any entities
    entities = er.async_entries_for_device(entity_registry, old_device.id)
    
    _LOGGER.debug(f"Legacy device has {len(entities)} entities")
    
    if not entities:
        _LOGGER.debug("Removing orphaned legacy 'palgate' device")
        device_registry.async_remove_device(old_device.id)
    else:
        _LOGGER.debug(f"Legacy device still has entities: {[e.entity_id for e in entities]}")

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
