"""
Utility functions

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


def galois_mul2(value: ctypes.c_uint8) -> ctypes.c_uint8:
    if value.value >> 7:
        return ctypes.c_uint8((value.value << 1) ^ 0x1b)
    else:
        return ctypes.c_uint8(value.value << 1)


def bytes_to_uint8(data: bytes) -> [ctypes.c_uint8]:
    return [ctypes.c_uint8(i) for i in data]


def uint8_to_bytes(data: [ctypes.c_uint8]) -> bytes:
    return bytes(i.value for i in data)
