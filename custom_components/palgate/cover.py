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

from .api import PalgateApiClient
from .const import DOMAIN as PALGATE_DOMAIN, CONF_PHONE_NUMBER

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Palgate entities from a config_entry."""

    COVERS: tuple[CoverEntityDescription, ...] = (
        CoverEntityDescription(
            key=entry.data[CONF_DEVICE_ID],
            name=entry.data[CONF_DEVICE_ID],
            icon="mdi:boom-gate-outline",
            device_class=CoverDeviceClass.GARAGE,
        ),
    )

    api = PalgateApiClient(
        device_id=entry.data[CONF_DEVICE_ID],
        token=entry.data[CONF_TOKEN],
        phone_number=entry.data[CONF_PHONE_NUMBER],
        session=async_get_clientsession(hass),
    )
        
    async_add_entities(
        PalgateCover(api, description) for description in COVERS
    )


class PalgateCover(CoverEntity):
    """Define a Palgate entity."""

    def __init__(
        self,
        api: PalgateApiClient,
        description: CoverEntityDescription,
    ) -> None:
        """Initialize."""

        self.api = api
        self.entity_description = description

        self._attr_unique_id = f"{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(PALGATE_DOMAIN, "palgate")},
            name="Palgate",
            model="Palgate",
            manufacturer="Palgate",
        )

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

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""

        await self.api.open_gate()
