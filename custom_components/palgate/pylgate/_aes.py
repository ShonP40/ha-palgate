"""
AES 128-bit encryption and decryption

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

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
import ctypes

from ._constants import S_BOX, RCON, INVERSE_S_BOX, BLOCK_SIZE, KEY_SIZE
from ._utils import galois_mul2, bytes_to_uint8, uint8_to_bytes


def aes_encrypt_decrypt(state: bytes, key: bytes, *, is_encrypt: bool) -> bytes:
    if len(state) != BLOCK_SIZE or len(key) != KEY_SIZE:
        raise ValueError("State and/or key are not 16 bytes")

    state_array = bytes_to_uint8(state)
    key_array = bytes_to_uint8(key)
    _aes_enc_dec(state_array, key_array, is_encrypt)

    return uint8_to_bytes(state_array)


def _aes_enc_dec(state: [ctypes.c_uint8], key: [ctypes.c_uint8], encrypt: bool) -> None:
    if encrypt:
        for rnd in range(10):
            key[0] = ctypes.c_uint8(S_BOX[key[13].value] ^ key[0].value ^ RCON[rnd])
            key[1] = ctypes.c_uint8(S_BOX[key[14].value] ^ key[1].value)
            key[2] = ctypes.c_uint8(S_BOX[key[15].value] ^ key[2].value)
            key[3] = ctypes.c_uint8(S_BOX[key[12].value] ^ key[3].value)
            for i in range(4, KEY_SIZE):
                key[i] = ctypes.c_uint8(key[i].value ^ key[i - 4].value)

        for i in range(BLOCK_SIZE):
            state[i] = ctypes.c_uint8(state[i].value ^ key[i].value)

    for rnd in range(10):
        if encrypt:
            for i in range(KEY_SIZE - 1, 3, -1):
                key[i] = ctypes.c_uint8(key[i].value ^ key[i - 4].value)
            key[0] = ctypes.c_uint8(S_BOX[key[13].value] ^ key[0].value ^ RCON[9 - rnd])
            key[1] = ctypes.c_uint8(S_BOX[key[14].value] ^ key[1].value)
            key[2] = ctypes.c_uint8(S_BOX[key[15].value] ^ key[2].value)
            key[3] = ctypes.c_uint8(S_BOX[key[12].value] ^ key[3].value)
        else:
            for i in range(BLOCK_SIZE):
                state[i] = ctypes.c_uint8(S_BOX[state[i].value ^ key[i].value])

            buf1 = state[1].value
            state[1].value = state[5].value
            state[5].value = state[9].value
            state[9].value = state[13].value
            state[13].value = buf1

            buf1, buf2 = state[2].value, state[6].value
            state[2].value = state[10].value
            state[6].value = state[14].value
            state[10].value = buf1
            state[14].value = buf2

            buf1 = state[15].value
            state[15].value = state[11].value
            state[11].value = state[7].value
            state[7].value = state[3].value
            state[3].value = buf1

        if (rnd > 0 and encrypt) or (rnd < 9 and not encrypt):
            for i in range(4):
                buf4 = i << 2
                if encrypt:
                    buf1 = galois_mul2(galois_mul2(ctypes.c_uint8(state[buf4].value ^ state[buf4 + 2].value))).value
                    buf2 = galois_mul2(galois_mul2(ctypes.c_uint8(state[buf4 + 1].value ^ state[buf4 + 3].value))).value
                    state[buf4].value ^= buf1
                    state[buf4 + 1].value ^= buf2
                    state[buf4 + 2].value ^= buf1
                    state[buf4 + 3].value ^= buf2

                buf1 = state[buf4].value ^ state[buf4 + 1].value ^ state[buf4 + 2].value ^ state[buf4 + 3].value
                buf2 = state[buf4].value
                buf3 = galois_mul2(ctypes.c_uint8(state[buf4].value ^ state[buf4 + 1].value)).value
                state[buf4].value = state[buf4].value ^ buf3 ^ buf1
                buf3 = galois_mul2(ctypes.c_uint8(state[buf4 + 1].value ^ state[buf4 + 2].value)).value
                state[buf4 + 1].value = state[buf4 + 1].value ^ buf3 ^ buf1
                buf3 = galois_mul2(ctypes.c_uint8(state[buf4 + 2].value ^ state[buf4 + 3].value)).value
                state[buf4 + 2].value = state[buf4 + 2].value ^ buf3 ^ buf1
                buf3 = galois_mul2(ctypes.c_uint8(state[buf4 + 3].value ^ buf2)).value
                state[buf4 + 3].value = state[buf4 + 3].value ^ buf3 ^ buf1

        if encrypt:
            buf1 = state[13].value
            state[13].value = state[9].value
            state[9].value = state[5].value
            state[5].value = state[1].value
            state[1].value = buf1

            buf1, buf2 = state[10].value, state[14].value
            state[10].value = state[2].value
            state[14].value = state[6].value
            state[2].value = buf1
            state[6].value = buf2

            buf1 = state[3].value
            state[3].value = state[7].value
            state[7].value = state[11].value
            state[11].value = state[15].value
            state[15].value = buf1

            for i in range(BLOCK_SIZE):
                state[i] = ctypes.c_uint8(INVERSE_S_BOX[state[i].value] ^ key[i].value)
        else:
            key[0] = ctypes.c_uint8(S_BOX[key[13].value] ^ key[0].value ^ RCON[rnd])
            key[1] = ctypes.c_uint8(S_BOX[key[14].value] ^ key[1].value)
            key[2] = ctypes.c_uint8(S_BOX[key[15].value] ^ key[2].value)
            key[3] = ctypes.c_uint8(S_BOX[key[12].value] ^ key[3].value)
            for i in range(4, KEY_SIZE):
                key[i] = ctypes.c_uint8(key[i].value ^ key[i - 4].value)

    if not encrypt:
        for i in range(BLOCK_SIZE):
            state[i] = ctypes.c_uint8(state[i].value ^ key[i].value)
