"""Palgate library."""

from http import HTTPStatus
import json
from typing import Any, Optional

from datetime import datetime, timedelta

import aiohttp
from voluptuous.error import Error

from .pylgate.token_generator import generate_token

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

    def url(self) -> str:
        """Build the url by extracting the gate number (:1 or :2, etc...) and set it in the outputNum"""
        device_id = self.device_id
        output_num = 1  # default

        if ':' in device_id:
            base_id, output = device_id.rsplit(':', 1)
            if output.isdigit():
                device_id = base_id
                output_num = int(output)

        return f"https://api1.pal-es.com/v1/bt/device/{device_id}/open-gate?openBy=100&outputNum={output_num}"

    def headers(self) -> dict:
        """Get headers"""

        temporal_token = generate_token(bytes.fromhex(self.token),int(self.phone_number),int(self.token_type))
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-us",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "User-Agent": "BlueGate/115 CFNetwork/1128.0.1 Darwin/19.6.0",
            "x-bt-token": f"{temporal_token}",
        }

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

        async with self._session.get(url=self.url(), headers=self.headers()) as resp:
            if resp.status == HTTPStatus.UNAUTHORIZED:
                raise Error(f"Unauthorized. {resp.status}")
            if resp.status != HTTPStatus.OK:
                error_text = json.loads(await resp.text())
                raise Error(f"Not OK {resp.status} {error_text}")

            self.next_open = datetime.now() + timedelta(seconds=self.seconds_to_open)
            self.next_closing = datetime.now() + timedelta(seconds=(self.seconds_to_open + self.seconds_open))
            self.next_closed = datetime.now() + timedelta(seconds=(self.seconds_to_open + self.seconds_open + self.seconds_to_close))

            return await resp.json()
    async def invert_gate(self) -> Any:
        """Trigger the Palgate device again during open"""

        if (self.allow_invert_as_stop and self.is_opening()):

            async with self._session.get(url=self.url(), headers=self.headers()) as resp:
                if resp.status == HTTPStatus.UNAUTHORIZED:
                    raise Error(f"Unauthorized. {resp.status}")
                if resp.status != HTTPStatus.OK:
                    error_text = json.loads(await resp.text())
                    raise Error(f"Not OK {resp.status} {error_text}")

                self.next_closing = datetime.now()
                self.next_closed = datetime.now() + timedelta(seconds=(self.seconds_to_close))  # Best guess

                return await resp.json()
