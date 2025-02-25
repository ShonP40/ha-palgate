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
            data_schema=self._create_schema(),
            errors={},
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        if user_input is not None:

            if user_input[CONF_DEVICE_ID] != self.device_id:
                return self.async_show_form(
                    step_id="reconfigure",
                    data_schema=self._create_schema(),
                    errors={"base":"cant_reconfigure_device_id"},
                )

            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )
        self.entry = self._get_reconfigure_entry()
        self.device_id = self.entry.data[CONF_DEVICE_ID]

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._create_schema(),
            errors={},
        )

    async def _async_existing_devices(self, area: str) -> bool:
        """Find existing devices."""

        existing_devices = [
            f"{entry.data.get(CONF_DEVICE_ID)}"
            for entry in self._async_current_entries()
        ]

        return area in existing_devices

    def _create_schema(self) -> vol.Schema:

        def_device_id  = self.entry.data[CONF_DEVICE_ID] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else None
        def_token      = self.entry.data[CONF_TOKEN] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else None
        def_phone      = self.entry.data[CONF_PHONE_NUMBER] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else None
        def_token_type = self.entry.data[CONF_TOKEN_TYPE] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else "1"
        def_sec_to_open  = self.entry.data[CONF_ADVANCED][CONF_SECONDS_TO_OPEN] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else SECONDS_TO_OPEN
        def_sec_open     = self.entry.data[CONF_ADVANCED][CONF_SECONDS_OPEN] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else SECONDS_OPEN
        def_sec_to_close = self.entry.data[CONF_ADVANCED][CONF_SECONDS_TO_CLOSE] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else SECONDS_TO_CLOSE
        def_allow_invert = self.entry.data[CONF_ADVANCED][CONF_ALLOW_INVERT_AS_STOP] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else False

        return vol.Schema(
        {
            vol.Required(CONF_DEVICE_ID, default=def_device_id): str,
            vol.Required(CONF_TOKEN, default=def_token): str,
            vol.Required(CONF_PHONE_NUMBER, default=def_phone): str,
            vol.Required(CONF_TOKEN_TYPE, default=def_token_type): selector({
                "select": {
                    "mode": "dropdown",
                    "options": ["0","1", "2"],
                }
            }),
            vol.Required(CONF_ADVANCED): section(
                vol.Schema(
                    {
                        vol.Required(CONF_SECONDS_TO_OPEN, default=def_sec_to_open): int,
                        vol.Required(CONF_SECONDS_OPEN, default=def_sec_open): int,
                        vol.Required(CONF_SECONDS_TO_CLOSE, default=def_sec_to_close): int,
                        vol.Required(CONF_ALLOW_INVERT_AS_STOP, default=def_allow_invert): bool,
                    }
                ),
                {"collapsed": True}
            )
        }
        )
