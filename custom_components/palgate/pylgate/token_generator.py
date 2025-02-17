"""
Logic for generating a derived token used by PalGate API

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import struct
import time

from ._constants import (
    BLOCK_SIZE,
    T_C_KEY,
    TOKEN_SIZE,
    TIMESTAMP_OFFSET,
)

from ._aes import aes_encrypt_decrypt

from .types import TokenType


def generate_token(session_token: bytes,
                   phone_number: int,
                   token_type: TokenType,
                   *,
                   timestamp_ms: int | None = None,
                   timestamp_offset: int = TIMESTAMP_OFFSET) -> str:
    """Generates a derived token for PalGate API
    Args:
        session_token (bytes): Base token generated either via SMS or Device Linking.
        phone_number (int): The phone number associated with `session_token` in international format.
            PalGate uses phone numbers as user IDs, referring to each user's phone number as their user id
        token_type (TokenType): `session_token`'s token type
        timestamp_ms (:obj:`int`, optional): time in seconds since Epoch. Defaults to current time
            The derived token is based on this timestamp, each token is valid for approximately 5 seconds
        timestamp_offset (:obj:`int`, optional): offset to add to `timestamp_ms`.
            Defaults to `TIMESTAMP_OFFSET` which is the value used by PalGate's official app

    Returns:
        str: The derived token as hex string

    Raises:
        ValueError: if `session_token` is not 16 bytes.
            if `phone_number` is not 12 digits
            if `token_type`'s value does not exist
    """
    if len(session_token) != BLOCK_SIZE:
        raise ValueError('Invalid session token')

    if timestamp_ms is None:
        timestamp_ms = int(time.time())

    step_2_key = _step_1(session_token, phone_number)

    step_2_result = _step_2(step_2_key, timestamp_ms, timestamp_offset)

    result = bytearray(TOKEN_SIZE)
    if token_type == TokenType.SMS:
        result[0] = 0x01
    elif token_type == TokenType.PRIMARY:
        result[0] = 0x11
    elif token_type == TokenType.SECONDARY:
        result[0] = 0x21
    else:
        raise ValueError(f'unknown token type: {token_type}')

    result[1] = (phone_number >> 0x28) & 0xff
    result[2] = (phone_number >> 0x20) & 0xff
    result[3] = (phone_number >> 0x18) & 0xff
    result[4:7] = struct.pack(">Q", phone_number)[5:8]

    result[7:23] = step_2_result

    return result.hex().upper()


def _step_1(session_token: bytes, phone_number: int) -> bytes:
    key = T_C_KEY.copy()
    key[6:12] = struct.pack('>Q', phone_number)[2:]

    return aes_encrypt_decrypt(session_token, bytes(key), is_encrypt=True)


def _step_2(result_from_step_1: bytes, timestamp_ms: int, timestamp_offset: int) -> bytes:
    next_state = bytearray(BLOCK_SIZE)
    next_state[1:3] = struct.pack('<H', 0xa0a)
    next_state[10:14] = struct.pack('>I', timestamp_ms + timestamp_offset)

    return aes_encrypt_decrypt(bytes(next_state), result_from_step_1, is_encrypt=False)
