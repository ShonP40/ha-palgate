"""Palgate library."""

from http import HTTPStatus
import json
from typing import Any, Optional

from datetime import datetime, timedelta

import aiohttp
from voluptuous.error import Error
import logging
from homeassistant.exceptions import HomeAssistantError

from .pylgate.token_generator import generate_token
from .const import *

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Output relay modes: maps friendly name -> (output#LatchStatus, output#Disabled)
RELAY_MODES: dict[str, tuple[bool, bool]] = {
    GATE_MODE_NORMAL:      (False, False),
    GATE_MODE_HOLD_OPEN:   (True,  True),
    GATE_MODE_HOLD_CLOSED:  (False, True),
}
RELAY_MODES_INVERSE: dict[tuple[bool, bool], str] = {
    v: k for k, v in RELAY_MODES.items()
}

class PalgateApiClient:
    """Main class for handling connection with."""

    def __init__(
        self,
        device_id: str,
        token: str,
        token_type: str,
        phone_number: str,
        seconds_to_open: int,
        seconds_open: int,
        seconds_to_close: int,
        allow_invert_as_stop: bool,
        session: Optional[aiohttp.client.ClientSession] = None,
    ) -> None:
        """Initialize connection with Palgate."""

        self._session = session
        self.device_id: str = device_id
        self.token: str = token
        self.token_type: str = token_type
        self.phone_number: str = phone_number
        self.seconds_to_open: int = seconds_to_open
        self.seconds_open: int = seconds_open
        self.seconds_to_close: int = seconds_to_close
        self.allow_invert_as_stop: bool = allow_invert_as_stop
        self.next_open: datetime = datetime.now()
        self.next_closing: datetime = datetime.now()
        self.next_closed: datetime = datetime.now()
        self.relay_mode_permitted: bool = False  # updated by get_relay_mode()

    def _parsed_device_id(self) -> tuple[str, int]:
        """Return (base_device_id, output_num), parsing any ':N' suffix."""
        device_id = self.device_id
        output_num = 1  # default

        if ':' in device_id:
            base_id, output = device_id.rsplit(':', 1)
            if output.isdigit():
                device_id = base_id
                output_num = int(output)

        return device_id, output_num

    def _open_url(self) -> str:
        """Build the base open-gate URL."""
        device_id, output_num = self._parsed_device_id()
        return (
            f"https://api1.pal-es.com/v1/bt/device/{device_id}"
            f"/open-gate?openBy=100&outputNum={output_num}"
        )

    def _headers(self) -> dict:
        """Get headers. Token generates dynamically as it includes a timestamp"""

        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-us",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "User-Agent": "BlueGate/115 CFNetwork/1128.0.1 Darwin/19.6.0",
            "x-bt-token": f"{generate_token(bytes.fromhex(self.token),
                            int(self.phone_number),
                            int(self.token_type))}",
        }

    async def _api_request(self, url: str) -> dict:
        """Execute a GET to any Palgate API URL, handle HTTP and API errors, return parsed JSON."""
        async with self._session.get(url=url, headers=self._headers()) as resp:
            _LOGGER.debug(f"API request. URL: {resp.url}")
            if resp.status == HTTPStatus.UNAUTHORIZED:
                raise HomeAssistantError(f"Unauthorized. {resp.status}")
            if resp.status != HTTPStatus.OK:
                raise HomeAssistantError(f"Not OK {resp.status} {await resp.text()}")
            reply = await resp.json()

        _LOGGER.debug(f"API response: {reply}")
        if reply.get("err"):
            raise HomeAssistantError(f"API Request Error: {reply.get('msg') or reply.get('err')}")
        
        return reply

    def is_opening(self) -> bool:
        """Current state of gate is opening."""
        
        return True if (self.next_open > datetime.now()) else False

    def is_closing(self) -> bool:
        """Current state of gate is closing."""
        
        return True if (self.next_closed > datetime.now() and self.next_closing < datetime.now()) else False

    def is_closed(self) -> bool:
        """Current state of gate is open."""

        return False if (self.next_closed > datetime.now()) else True

    async def open_gate(self) -> Any:
        """Open Palgate device."""

        reply = await self._api_request(self._open_url())
        self.next_open    = datetime.now() + timedelta(seconds=self.seconds_to_open)
        self.next_closing = datetime.now() + timedelta(seconds=(self.seconds_to_open + self.seconds_open))
        self.next_closed  = datetime.now() + timedelta(seconds=(self.seconds_to_open + self.seconds_open + self.seconds_to_close))
        return reply

    async def invert_gate(self) -> Any:
        """Trigger the Palgate device again during open"""

        if self.allow_invert_as_stop and self.is_opening():
            reply = await self._api_request(self._open_url())
            self.next_open = self.next_closing = datetime.now()
            self.next_closed  = datetime.now() + timedelta(seconds=self.seconds_to_close)  # Best guess
            return reply

    async def get_device_data(self) -> dict:
        """Fetch full device data from the API."""
        device_id, _ = self._parsed_device_id()
        url = f"https://api1.pal-es.com/v1/bt/device/{device_id}"
        data = await self._api_request(url)
        return data.get("device", data)
        
    async def get_relay_mode(self) -> str:
        device_id, output_num = self._parsed_device_id()

        device = await self.get_device_data()

        self.relay_mode_permitted = bool(device.get(f"output{output_num}Latch", False))

        latch = device.get(f"output{output_num}LatchStatus", False)
        dsbl  = device.get(f"output{output_num}Disabled",    False)
        return RELAY_MODES_INVERSE.get((latch, dsbl), GATE_MODE_NORMAL)

    async def set_relay_mode(self, mode: str) -> None:
        """Set the output relay mode. mode must be a key in RELAY_MODES."""

        latch, dsbl = RELAY_MODES[mode]
        device_id, output_num = self._parsed_device_id()
        url = (
            f"{self._open_url()}"
            f"&output{output_num}LatchStatus={str(latch).lower()}"
            f"&output{output_num}Disabled={str(dsbl).lower()}"
        )

        await self._api_request(url)
