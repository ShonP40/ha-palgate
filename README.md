# Palgate Home Assistant integration

![GitHub Release](https://img.shields.io/github/v/release/ShonP40/ha-palgate?style=flat-square)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Unofficial integration, use at your own risk!

## Extracting the token
You will need to run the following command on your Home Assistant server using SSH/the terminal addon to extract your Palgate session token:

```shell
/config/custom_components/palgate/generate_linked_device_session_token.sh
```

## Installation

1. Ensure that [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository
3. Search for and install the "Palgate" integration
4. Restart Home Assistant
5. Configure the `Palgate` integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ShonP40&repository=ha-palgate&category=Integration)

## Configuration

1. `Device ID` - This is your physical Palgate device ID, can be obtained from the settings page of each gate in the Palgate app
2. `Phone Number` - This is the phone number registered on Palgate (e.g.: `972505555555`)
3. `Token` - The session token obtained as explained above, via the `Link Device` button in the Palgate app
4. `Linked Device Number` - This should either be `1` or `2`, depending on whether you have another device linked (other than HA) to your Palgate account

## Advanced Configuration
1. `Time (sec) gate takes to open` - The time it takes for the gate to open in seconds
2. `Time (sec) gate remains open` - The time the gate remains open in seconds
3. `Time (sec) gate takes to close` - The time it takes for the gate to close in seconds
4. `Allow triggering gate while opening, to invert direction` - If enabled, the gate can be triggered while opening to invert the direction

## Features
### Cover
- Open
- Custom open/close timouts

## Notes
- Palgate's API does not report the position of the gate

## Credits
- [sindrebroch](https://github.com/sindrebroch) - Original creator
- [DonutByte](https://github.com/DonutByte) - [Python implementation with an updated time-sensitive token generator](https://github.com/DonutByte/pylgate)
- [doron1](https://github.com/doron1) - [Implemented support for time-sensitive tokens](https://github.com/ShonP40/ha-palgate/pull/4)
