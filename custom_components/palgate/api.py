"""Palgate library."""

from http import HTTPStatus
import json
from typing import Any, Optional

from datetime import datetime, timedelta

import aiohttp
from voluptuous.error import Error

from .pylgate.token_generator import generate_token

from .const import (
    SECONDS_OPEN,
    SECONDS_TO_OPEN,
    SECONDS_TO_CLOSE,
)

class PalgateApiClient:
    """Main class for handling connection with."""

    def __init__(
        self,
        device_id: str,
        token: str,
        token_type: str,
        phone_number: str,
        session: Optional[aiohttp.client.ClientSession] = None,
    ) -> None:
        """Initialize connection with Palgate."""

        self._session = session
        self.device_id: str = device_id
        self.token: str = token
        self.token_type: str = token_type
        self.phone_number: str = phone_number

        self.next_open: datetime = datetime.now()
        self.next_closing: datetime = datetime.now()
        self.next_closed: datetime = datetime.now()

    def url(self) -> str:
        return f"https://api1.pal-es.com/v1/bt/device/{self.device_id}/open-gate?openBy=100&outputNum=1"

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

            self.next_open = datetime.now() + timedelta(seconds=SECONDS_TO_OPEN)
            self.next_closing = datetime.now() + timedelta(seconds=(SECONDS_TO_OPEN + SECONDS_OPEN))
            self.next_closed = datetime.now() + timedelta(seconds=(SECONDS_TO_OPEN + SECONDS_OPEN + SECONDS_TO_CLOSE))

            return await resp.json()
