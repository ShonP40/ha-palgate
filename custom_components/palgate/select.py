"""Select platform for Palgate relay mode."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import PalgateApiClient, RELAY_MODES
from .const import DOMAIN as PALGATE_DOMAIN
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Palgate mode select entity from a config entry."""

    device_id = entry.data[CONF_DEVICE_ID]

    api = PalgateApiClient(
        device_id=device_id,
        token=entry.data[CONF_TOKEN],
        token_type=entry.data[CONF_TOKEN_TYPE],
        phone_number=entry.data[CONF_PHONE_NUMBER],
        seconds_to_open=entry.data[CONF_ADVANCED][CONF_SECONDS_TO_OPEN],
        seconds_open=entry.data[CONF_ADVANCED][CONF_SECONDS_OPEN],
        seconds_to_close=entry.data[CONF_ADVANCED][CONF_SECONDS_TO_CLOSE],
        allow_invert_as_stop=entry.data[CONF_ADVANCED][CONF_ALLOW_INVERT_AS_STOP],
        session=async_get_clientsession(hass),
    )

    async_add_entities([PalgateRelayModeSelect(api, device_id)], update_before_add=True)


class PalgateRelayModeSelect(SelectEntity):
    """Select entity for the Palgate output relay mode."""

    _attr_has_entity_name                 = True
    _attr_options                         = list(RELAY_MODES.keys())
    # _attr_icon                            = "mdi:boom-gate-up"
    _attr_entity_registry_enabled_default = False
    translation_key                       = "relay_mode"
    scan_interval                         = SCAN_INTERVAL

    def __init__(
        self,
        api: PalgateApiClient,
        device_id: str,
    ) -> None:
        """Initialize."""
        self.api = api
        self._attr_unique_id   = f"{device_id}_relay_mode"
        self._attr_device_info = DeviceInfo(
            identifiers={(PALGATE_DOMAIN, device_id)},
        )
        self._attr_current_option: str | None = None
        self._attr_available: bool = False

    async def async_update(self) -> None:
        """Fetch current relay mode and permission flag from the device."""

        try:
            self._attr_current_option = await self.api.get_relay_mode()
            self._attr_available      = self.api.relay_mode_permitted

        except Exception as exc:
            _LOGGER.error("Failed to fetch relay mode for %s: %s", self.unique_id, exc)
            self._attr_available = False

    async def async_select_option(self, option: str) -> None:
        """Handle user selecting a new relay mode."""
        await self.api.set_relay_mode(option)
        self._attr_current_option = option
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        if self._attr_current_option in (GATE_MODE_HOLD_OPEN, GATE_MODE_HOLD_CLOSED):
            return "mdi:block-helper"
        return "mdi:boom-gate-up"  # normal / default
