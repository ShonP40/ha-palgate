"""Config flow for Palgate integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult, section
from homeassistant.helpers.selector import selector

from .const import DOMAIN as PALGATE_DOMAIN
from .const import *

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): str,
        vol.Required(CONF_TOKEN): str,
        vol.Required(CONF_PHONE_NUMBER): str,
        vol.Required(CONF_TOKEN_TYPE, default="1"): selector({
            "select": {
                "mode": "dropdown",
                "options": ["0","1", "2"],
            }
        }),
        vol.Required("advanced_options"): section(
            vol.Schema(
                {
                    vol.Required(CONF_SECONDS_TO_OPEN, default=SECONDS_TO_OPEN): int,
                    vol.Required(CONF_SECONDS_OPEN, default=SECONDS_OPEN): int,
                    vol.Required(CONF_SECONDS_TO_CLOSE, default=SECONDS_TO_CLOSE): int,
                    vol.Required(CONF_ALLOW_INVERT_AS_STOP, default=False): bool,
                }
            ),
            {"collapsed": True}
        )
    }
)

class PollenvarselFlowHandler(config_entries.ConfigFlow, domain=PALGATE_DOMAIN):
    """Config flow for Palgate."""

    VERSION = 3

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        if user_input is not None:

            device_id: str = user_input[CONF_DEVICE_ID]

            if await self._async_existing_devices(device_id):
                return self.async_abort(reason="already_configured")

            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=device_id.title(),
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=SCHEMA,
            errors={},
        )

    async def _async_existing_devices(self, area: str) -> bool:
        """Find existing devices."""

        existing_devices = [
            f"{entry.data.get(CONF_DEVICE_ID)}"
            for entry in self._async_current_entries()
        ]

        return area in existing_devices
