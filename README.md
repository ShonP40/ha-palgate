# Palgate Home Assistant integration

![GitHub Release](https://img.shields.io/github/v/release/ShonP40/ha-palgate?style=flat-square)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Unofficial integration, use at your own risk!

## Extracting the token
You will need to run the following command on your Home Assistant server using SSH/the terminal addon to extract your Palgate session token:

```shell
/config/custom_components/palgate/generate_linked_device_token.sh
```

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository
3. Search for and install the "Palgate" integration
4. Restart Home Assistant
5. Configure the `Palgate` integration

### Manual

1. Download the `Source code (zip)` file from the [latest release](https://github.com/ShonP40/ha-palgate/releases/latest)
2. Unpack the release and copy the `custom_components/ha-palgate` directory into the `custom_components` directory of your Home Assistant installation
3. Restart Home Assistant
4. Configure the `Palgate` integration

## Configuration

1. Device ID - This is your physical Palgate device ID, can be obtained from the settings page of each gate in the Palgate app
2. Phone Number - This is the phone number registered on Palgate (e.g.: `972505555555`)
3. Token - The session token obtained as explained above, via the `Link Device` button in the Palgate app
4. Linked Device Number - This should either be `1` or `2`, depending on whether you have another device linked (other than HA) to your Palgate account

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
