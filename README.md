# Palgate Home Assistant integration

![GitHub Release](https://img.shields.io/github/v/release/ShonP40/ha-palgate?style=flat-square)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Unofficial integration, use at your own risk!

This integration makes use of [the amazing work](https://github.com/DonutByte/pylgate) of [@DonutByte](https://github.com/DonutByte) for generating time-sensitive tokens for Palgate.

## Requirements
You will need to [obtain a session token](https://github.com/DonutByte/pylgate/blob/main/examples/generate_linked_device_session_token.py). This is done once, using the Palgate app, via "Link Devices".
Note that "sniffing a token", that was possible in the past, does not work anymore due to changes in the Palgate software. Similarly, the current mechanism may or may not work in the future, depending on Palgate's API. As mentioned, use at your own risk.
## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository
3. Search for and install the "Palgate" integration
4. Restart Home Assistant
5. Configure the `Palgate` integration

### MANUAL INSTALLATION

1. Download the `Source code (zip)` file from the [latest release](https://github.com/ShonP40/ha-palgate/releases/latest)
2. Unpack the release and copy the `custom_components/ha-palgate` directory into the `custom_components` directory of your Home Assistant installation
3. Restart Home Assistant
4. Configure the `Palgate` integration

## Configuration

You need to configure 3 items:
1. Device ID - This is your physical Palgate device ID, can be obtained from the Palgate app ("settings" of the specific gate)
2. Phone Number - This is the phone number recognized by Palgate. e.g.: 972505555555
3. Token - The session token obtained as explained above, via Link Device.

## Todo
- [ ] Add ability to customize open and close timeouts

## Features
### Cover
- Open

## Notes
- Palgate's API does not report the position of the gate

- This fork was made to preserve this code for anyone that's still using it since the original creator ([sindrebroch](https://github.com/sindrebroch)) kept randomly making [his repo](https://github.com/sindrebroch/ha-palgate) private
