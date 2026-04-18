"""Sensor file for Palgate."""

from typing import Any, Optional

from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityDescription,
    CoverDeviceClass,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import ServiceValidationError
import logging

from .api import PalgateApiClient
from .const import DOMAIN as PALGATE_DOMAIN
from .const import *

_LOGGER: logging.Logger = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Palgate entities from a config_entry."""

    device_id = entry.data[CONF_DEVICE_ID]
    
    COVERS: tuple[CoverEntityDescription, ...] = (
        CoverEntityDescription(
            key=device_id,
            name=device_id,
            icon="mdi:boom-gate-outline",
            device_class=CoverDeviceClass.GARAGE,
        ),
    )

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
        
    async_add_entities(
        PalgateCover(api, description, device_id) for description in COVERS
    )


class PalgateCover(CoverEntity):
    """Define a Palgate entity."""

    def __init__(
        self,
        api: PalgateApiClient,
        description: CoverEntityDescription,
        device_id: str,
    ) -> None:
        """Initialize."""

        self.api = api
        self.entity_description = description

        self._attr_unique_id = f"{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(PALGATE_DOMAIN, device_id)},
            name=device_id,
            manufacturer="Palgate",
            model="Gate Controller",
        )

        self._address: str | None = None
        self._address_coord: tuple[str, str] | None = None
        self._sim_status: str | None = None
        self._sim_valid_until: str | None = None
        self._model: str | None = None
        self._isadmin: bool | None = None
        self._name1: str | None = None
        self._customname1: str | None = None
        self._customname2: str | None = None

    @property
    def is_opening(self) -> Optional[bool]:
        """Return if the cover is opening or not."""
        return self.api.is_opening()

    @property
    def is_closing(self) -> Optional[bool]:
        """Return if the cover is closing or not."""
        return self.api.is_closing()

    @property
    def is_closed(self) -> Optional[bool]:
        """Return if the cover is closed or not."""
        return self.api.is_closed()

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "address":         self._address,
            "sim_status":      self._sim_status,
            "sim_valid_until": self._sim_valid_until,
            "model":           self._model,
            "isadmin":         self._isadmin,
            "address_coord":   self._address_coord,
            "name1":           self._name1,
            "customname1":     self._customname1,
            "customname2":     self._customname2,
        }

    async def async_added_to_hass(self) -> None:
        """Fetch device info once on startup."""
        try:
            device = await self.api.get_device_data()
            self._address         = device.get("address")
            self._sim_status      = device.get("simStatus")
            self._sim_valid_until = device.get("validUntil")
            self._model           = device.get("model")
            self._address_coord   = device.get("addressCoord")
            self._isadmin         = device.get("admin")
            self._name1           = device.get("name1")
            self._customname1     = device.get("customName1")
            self._customname2     = device.get("customName2")
            self.async_write_ha_state()
        except Exception as exc:
            _LOGGER.warning("Failed to fetch device info: %s", exc)

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""

        try:
            await self.api.open_gate()
        except Exception as exc:
            _LOGGER.warning("Gate operation failed. %s", exc)
            raise ServiceValidationError(str(exc)) from exc

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover - only if allowed in config (usually auto-close)"""

        try:
            await self.api.invert_gate()
        except Exception as exc:
            _LOGGER.warning("Gate operation failed. %s", exc)
            raise ServiceValidationError(str(exc)) from exc
