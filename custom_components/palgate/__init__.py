"""The Palgate integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.const import CONF_DEVICE_ID, CONF_TOKEN
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
import logging

from .api import PalgateApiClient
from .const import DOMAIN as PALGATE_DOMAIN
from .const import *

_LOGGER: logging.Logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Service schemas - intentionally lean; user record fields are
# passed through opaquely via "settings" to avoid coupling our
# code to the Palgate API's user record structure.
# ------------------------------------------------------------------

_ENTITY_FIELD   = {vol.Required("entity_id"): cv.entity_id}
_PHONE_FIELD    = {vol.Required("phone"): cv.string}
_SETTINGS_FIELD = {vol.Optional("settings"): dict}

_SVC_GET_DEVICE_USERS  = vol.Schema({**_ENTITY_FIELD})
_SVC_GET_USER_SETTINGS = vol.Schema({**_ENTITY_FIELD, **_PHONE_FIELD})
_SVC_ADD_USER          = vol.Schema({**_ENTITY_FIELD, **_PHONE_FIELD, **_SETTINGS_FIELD})
_SVC_REMOVE_USER       = vol.Schema({**_ENTITY_FIELD, **_PHONE_FIELD})
_SVC_SET_USER_SETTINGS = vol.Schema({**_ENTITY_FIELD, **_PHONE_FIELD, **_SETTINGS_FIELD})
_SVC_GET_DEVICE_LOG    = vol.Schema({**_ENTITY_FIELD})


def _get_api(hass: HomeAssistant, entity_id: str) -> PalgateApiClient:
    """Resolve a cover entity_id to its shared PalgateApiClient."""

    entry_id = er.async_get(hass).async_get(entity_id).config_entry_id

    entry_data = hass.data.get(PALGATE_DOMAIN, {}).get(entry_id)
    if not entry_data:
        raise ServiceValidationError(f"No Palgate data found for {entity_id}")
    return entry_data[DATA_API]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Palgate from a config entry."""

    _LOGGER.debug(f"Setting up Palgate config entry: {entry.entry_id}, device_id: {entry.data[CONF_DEVICE_ID]}")

    # Shared API client - used by platforms and services
    api = PalgateApiClient(
        device_id=entry.data[CONF_DEVICE_ID],
        token=entry.data[CONF_TOKEN],
        token_type=entry.data[CONF_TOKEN_TYPE],
        phone_number=entry.data[CONF_PHONE_NUMBER],
        seconds_to_open=entry.data[CONF_ADVANCED][CONF_SECONDS_TO_OPEN],
        seconds_open=entry.data[CONF_ADVANCED][CONF_SECONDS_OPEN],
        seconds_to_close=entry.data[CONF_ADVANCED][CONF_SECONDS_TO_CLOSE],
        allow_invert_as_stop=entry.data[CONF_ADVANCED][CONF_ALLOW_INVERT_AS_STOP],
        session=async_get_clientsession(hass),
    )

    hass.data.setdefault(PALGATE_DOMAIN, {})
    hass.data[PALGATE_DOMAIN][entry.entry_id] = {DATA_API: api}

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

    # Register services (HA ignores duplicate registration - safe on reload)
    _register_services(hass)

    # Try to cleanup orphaned legacy multi-gate device (idempotent, safe to call multiple times)
    await _cleanup_orphaned_device(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[PALGATE_DOMAIN].pop(entry.entry_id, None)

    # Unregister services when the last entry is gone
    if not hass.data.get(PALGATE_DOMAIN):
        _unregister_services(hass)

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


# ------------------------------------------------------------------
# Service registration
# ------------------------------------------------------------------

def _register_services(hass: HomeAssistant) -> None:
    """Register Palgate services. Safe to call multiple times."""

    async def handle_get_device_users(call: ServiceCall) -> dict:
        """Return the full authorized user list, paginating transparently."""

        api = _get_api(hass, call.data["entity_id"])

        page      = await api.get_users_page(skip=0, limit=50)
        total     = page.get("count", 0)
        all_users = list(page.get("users", []))
        skip      = len(all_users)

        while skip < total:
            page  = await api.get_users_page(skip=skip, limit=50)
            batch = page.get("users", [])
            if not batch:
                break
            all_users.extend(batch)
            skip += len(batch)

        return {"count": total, "users": all_users}

    async def handle_get_user_settings(call: ServiceCall) -> dict:
        """Return the raw user record for a single user."""

        api = _get_api(hass, call.data["entity_id"])
        try:
            return await api.get_user(call.data["phone"])
        except HomeAssistantError as exc:
            raise ServiceValidationError(str(exc)) from exc

    async def handle_add_user(call: ServiceCall) -> dict:
        """Add a new authorized user."""

        api = _get_api(hass, call.data["entity_id"])
        try:
            return await api.add_user(
                call.data["phone"],
                settings=call.data.get("settings"),
            )
        except HomeAssistantError as exc:
            raise ServiceValidationError(str(exc)) from exc

    async def handle_remove_user(call: ServiceCall) -> dict:
        """Remove an authorized user."""

        api = _get_api(hass, call.data["entity_id"])
        try:
            return await api.remove_user(call.data["phone"])
        except HomeAssistantError as exc:
            raise ServiceValidationError(str(exc)) from exc

    async def handle_set_user_settings(call: ServiceCall) -> dict:
        """Update settings for an existing user."""

        api   = _get_api(hass, call.data["entity_id"])
        try:
            return await api.set_user_settings(
                phone=call.data["phone"],
                settings=call.data.get("settings"),
            )
        except HomeAssistantError as exc:
            raise ServiceValidationError(str(exc)) from exc

    async def handle_get_device_log(call: ServiceCall) -> dict:
        """Return the gate access log."""
        api = _get_api(hass, call.data["entity_id"])
        try:
            return await api.get_device_log()
        except HomeAssistantError as exc:
            raise ServiceValidationError(str(exc)) from exc

    hass.services.async_register(
        PALGATE_DOMAIN, SERVICE_GET_DEVICE_USERS,
        handle_get_device_users,
        schema=_SVC_GET_DEVICE_USERS,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        PALGATE_DOMAIN, SERVICE_GET_USER_SETTINGS,
        handle_get_user_settings,
        schema=_SVC_GET_USER_SETTINGS,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        PALGATE_DOMAIN, SERVICE_ADD_USER,
        handle_add_user,
        schema=_SVC_ADD_USER,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        PALGATE_DOMAIN, SERVICE_REMOVE_USER,
        handle_remove_user,
        schema=_SVC_REMOVE_USER,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        PALGATE_DOMAIN, SERVICE_SET_USER_SETTINGS,
        handle_set_user_settings,
        schema=_SVC_SET_USER_SETTINGS,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        PALGATE_DOMAIN, SERVICE_GET_DEVICE_LOG,
        handle_get_device_log,
        schema=_SVC_GET_DEVICE_LOG,
        supports_response=SupportsResponse.ONLY,
)

def _unregister_services(hass: HomeAssistant) -> None:
    """Unregister all Palgate services."""
    for service in (
        SERVICE_GET_DEVICE_USERS,
        SERVICE_GET_USER_SETTINGS,
        SERVICE_ADD_USER,
        SERVICE_REMOVE_USER,
        SERVICE_SET_USER_SETTINGS,
        SERVICE_GET_DEVICE_LOG,
    ):
        hass.services.async_remove(PALGATE_DOMAIN, service)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _cleanup_orphaned_device(hass: HomeAssistant) -> None:
    """Remove the old shared 'Palgate' device if it's orphaned."""

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    _LOGGER.debug("Checking for orphaned legacy 'palgate' device...")

    old_device = device_registry.async_get_device(
        identifiers={(PALGATE_DOMAIN, "palgate")}
    )

    if not old_device:
        _LOGGER.debug("No legacy 'palgate' device found")
        return

    _LOGGER.debug(f"Found legacy (multi-gate) device: {old_device.id}, config_entries: {old_device.config_entries}")

    entities = er.async_entries_for_device(entity_registry, old_device.id)

    _LOGGER.debug(f"Legacy device has {len(entities)} entities")

    if not entities:
        _LOGGER.debug("Removing orphaned legacy 'palgate' device")
        device_registry.async_remove_device(old_device.id)
    else:
        _LOGGER.debug(f"Legacy device still has entities: {[e.entity_id for e in entities]}")