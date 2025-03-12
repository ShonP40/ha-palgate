"""Config flow for Palgate integration."""

from __future__ import annotations

from typing import Any
import logging
import asyncio
import uuid
import pyqrcode
import io
import json
import aiohttp
from http import HTTPStatus

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult, section
from homeassistant.helpers.selector import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import HomeAssistantError 

from .const import DOMAIN as PALGATE_DOMAIN
from .const import *

_LOGGER = logging.getLogger(__name__)

class PollenvarselFlowHandler(config_entries.ConfigFlow, domain=PALGATE_DOMAIN):
    """Config flow for Palgate."""

    VERSION = 3

    def __init__(self):

        self._task: asyncio.Task[None] | None = None
        self.linking_code: str = None

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

            self.user_input = user_input
            
            if user_input[CONF_PHONE_NUMBER] == CONF_LINK_NEW_DEVICE:
                return await self.async_step_create_linked_device(
                    user_input=user_input,
                )
            else:
                self._linked_phone_number = user_input[CONF_PHONE_NUMBER]
                self._linked_token = \
                    self.current_linked_devices[
                        user_input[CONF_PHONE_NUMBER]][0]
                self._linked_token_type = \
                    self.current_linked_devices[
                        user_input[CONF_PHONE_NUMBER]][1]

            return await self.async_step_complete_new_entry()
            
            return self.async_create_entry(
                title=device_id.title(),
                data=user_input,
            )

        if self._task:              # Are we creating a new Linked Device?

            if self._task.done():

                return self.async_show_progress_done(
                    next_step_id="complete_new_entry"
                    )

            _LOGGER.debug("Link task not done. Keep spinning")
            # Task not done, keep waiting
            return await self.async_step_create_linked_device(
                user_input=user_input,
            )

        # Prepare form: Make a dict of all currently linked phones + tokens
        self.current_linked_devices = {}
        for entry in self._async_current_entries():
            if entry.domain == PALGATE_DOMAIN:
                self.current_linked_devices[entry.data[CONF_PHONE_NUMBER]] = \
                    [entry.data[CONF_TOKEN], entry.data[CONF_TOKEN_TYPE]]

        return self.async_show_form(
            step_id="user",
            data_schema=self._create_schema(),
            errors={},
        )

    async def async_step_complete_new_entry(
        self, user_input: dict[str, Any] | None = None
        ) -> FlowResult:

        if self._task:
            if _exc := self._task.exception():

                _LOGGER.error(_exc)
                return self.async_abort(reason=_exc.args[0])

        self.user_input[CONF_PHONE_NUMBER] = self._linked_phone_number
        self.user_input[CONF_TOKEN] = self._linked_token
        self.user_input[CONF_TOKEN_TYPE] = self._linked_token_type

        return self.async_create_entry(
            title=self.user_input[CONF_DEVICE_ID].title(),
            data=self.user_input,
        )

    async def async_step_create_linked_device(
        self, user_input: dict[str, Any] | None = None
        ) -> FlowResult:

        if not self.linking_code:
            self.linking_code = str(uuid.uuid4())

            # Generate a QR code for Palgate Device Linking 
            self._qr_img_str = pyqrcode.create(
                f'{{"id": "{self.linking_code}"}}',
                error='L'
            ).png_as_base64_str(
                scale=15, 
                quiet_zone=4
            )

            # Fire off a backend task that waits for vendor API confirmation
            # of user scanning the QR code
            self._task = self.hass.async_create_task(
                self._wait_device_linking()
                )

        # Show form with progress spinner until linking completes
        return self.async_show_progress(
            progress_action="wait_for_qr",
            progress_task=self._task,
            description_placeholders={
                "qr_code": 
                f"<img src='data:image/png;base64,{self._qr_img_str}' />"
            },
        )

    # Wait for linking confirmation and token from vendor. Runs as asyncio.task
    async def _wait_device_linking(self):

        _session = async_get_clientsession(self.hass)

        _url = 'https://api1.pal-es.com/v1/bt/un/secondary/init/' +\
            f'{self.linking_code}'

        # Work around an apparent HASS quirk, - when show_progress is called
        # and the task is already done (e.g. exception), show_progress
        # spins forever. Wait a sec to let show_progress kick in before us :-(
        await asyncio.sleep(1)

        async with _session.get(
            url=_url
            ) as resp:

            if resp.status == HTTPStatus.UNAUTHORIZED:
                raise Exception(f"Unauthorized. {resp.status}")

            if resp.status != HTTPStatus.OK:
                raise Exception(f"Not OK {resp.status} {await resp.text()}")

            try:
                _response = json.loads(_text := await resp.text())

            except json.JSONDecodeError:
                _LOGGER.error("Link new dev, vendor response not valid JSON:")
                _LOGGER.error(_text)
                raise HomeAssistantError("Response from vendor not valid JSON")

        self._linked_phone_number = _response["user"]["id"]
        self._linked_token = _response["user"]["token"]
        self._linked_token_type = _response["secondary"]
        self._linked_status = _response["status"]
    
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
        def_sec_to_open  = \
            self.entry.data[CONF_ADVANCED][CONF_SECONDS_TO_OPEN] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else SECONDS_TO_OPEN
        def_sec_open     = \
            self.entry.data[CONF_ADVANCED][CONF_SECONDS_OPEN] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else SECONDS_OPEN
        def_sec_to_close = \
            self.entry.data[CONF_ADVANCED][CONF_SECONDS_TO_CLOSE] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else SECONDS_TO_CLOSE
        def_allow_invert = \
            self.entry.data[CONF_ADVANCED][CONF_ALLOW_INVERT_AS_STOP] \
            if self.source == config_entries.SOURCE_RECONFIGURE \
            else False

        _schema = vol.Schema(
        {
            vol.Required(CONF_DEVICE_ID, default=def_device_id): str,
        })

        if not self.source == config_entries.SOURCE_RECONFIGURE:
            _schema = _schema.extend(
                {
                vol.Required(CONF_PHONE_NUMBER): selector({
                    "select": {
                        "mode": "dropdown",
                        "options": list(self.current_linked_devices.keys()) + 
                            [ CONF_LINK_NEW_DEVICE ],
                    }
                })
            })

        _schema = _schema.extend(
            {
            vol.Required(CONF_ADVANCED): section(
                vol.Schema(
                    {
                        vol.Required(CONF_SECONDS_TO_OPEN, 
                            default=def_sec_to_open): int,
                        vol.Required(CONF_SECONDS_OPEN, 
                            default=def_sec_open): int,
                        vol.Required(CONF_SECONDS_TO_CLOSE,
                            default=def_sec_to_close): int,
                        vol.Required(CONF_ALLOW_INVERT_AS_STOP, 
                            default=def_allow_invert): bool,
                    }
                ),
                {"collapsed": False \
                    if self.source == config_entries.SOURCE_RECONFIGURE 
                    else True
                }
                )
            })

        return _schema
