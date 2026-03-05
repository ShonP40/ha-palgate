# Palgate Home Assistant integration

![GitHub Release](https://img.shields.io/github/v/release/doron1/ha-palgate?style=flat-square)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Unofficial integration, use at your own risk!

## Note for Release 1.4.x

As of release 1.4 of this integration, each gate is set up as a separate device, with a single "cover" type control. In previous releases, if you added multiple gates, they were all created as multiple "cover" entities under one device. The new setup allows for better control of multiple gates, e.g. assigning them to different areas.

The entity names for the gates remain the same, so existing automations, scripts or scenes *should* continue functioning as before, but it is advised to double check that everything still works as planned.

## Administrivia - New Maintainer

As of 5 March 2026, I ([doron1](https://github.com/doron1)) will be taking over as maintainer of this repo. On behalf of the Palgate users' community I'd like to express deep gratitudes to [@ShonP40](https://github.com/ShonP40), who provided an excellent home and ongoing code maintainance to this integration for quite a few years, enabling the rest of us to control our home, community or municipal gates via Home Assistant.

## Installation

1. Ensure that [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository
3. Search for and install the "Palgate" integration
4. Restart Home Assistant
5. Configure the `Palgate` integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=doron1&repository=ha-palgate&category=Integration)

## Configuration

1. `Device ID` - This is your physical Palgate device ID, can be obtained from the settings page of each gate in the Palgate app
2. `Linked Phone Number` - Lists the phone numbers of the Palgate accounts you linked

## Advanced Configuration
1. `Time (sec) gate takes to open` - The time it takes for the gate to open in seconds
2. `Time (sec) gate remains open` - The time the gate remains open in seconds
3. `Time (sec) gate takes to close` - The time it takes for the gate to close in seconds
4. `Allow triggering gate while opening, to invert direction` - If enabled, the gate can be triggered while opening to invert the direction

## Features
### Cover
- Open
- Stop (in most gates, invert movement)
- Custom open/close timeouts

## Notes
- Palgate's API does not report the position of the gate. Practically, this means that Home Assistant does not have definite knowledge of the gate being closed, or actively moving, or current position. This in turn means that the indications of "opening", "closed" etc. are simulated, primarily based on your configured numbers (see [Advanced Configuration](#advanced-configuration) above).

## Credits
- [sindrebroch](https://github.com/sindrebroch) - Original creator
- [ShonP40](https://github.com/ShonP40) - Devoted owner/maintainer of this integration for many years
- [DonutByte](https://github.com/DonutByte) - [Python implementation with an updated time-sensitive token generator](https://github.com/DonutByte/pylgate)
- [doron1](https://github.com/doron1) - [Implemented support for time-sensitive tokens](https://github.com/doron1/ha-palgate/pull/4), [Add Configurable Options](https://github.com/doron1/ha-palgate/pull/8), [Perform Full Device Linking in Config Flow](https://github.com/doron1/ha-palgate/pull/17), [One Device Per Gate](https://github.com/doron1/ha-palgate/pull/24) and more
- [bondar](https://github.com/bondar) - [Implemented support for devices that control multiple gates](https://github.com/doron1/ha-palgate/pull/18)
