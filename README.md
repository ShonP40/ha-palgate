# Palgate Home Assistant integration

![GitHub Release](https://img.shields.io/github/v/release/doron1/ha-palgate?style=flat-square)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

This is a Home Assistant integration for Palgate gate controllers. It creates a gate/cover entity in Home Assistant, allowing for gate control from HA dashboards and automations.

This is an unofficial integration, use at your own risk.


## Installation

1. Ensure that [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository
3. Search for and install the "Palgate" integration
4. Restart Home Assistant
5. Configure the `Palgate` integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=doron1&repository=ha-palgate&category=Integration)

## Configuration

This integration needs the Palgate app to be installed on your phone (Android or iOS). When adding your first gate, you will be guided through the process of linking your Palgate app to Home Assistant. Note that the Palgate app typically allows up to two Linked Devices. Once the linking is successful, you will be guided to complete the gate selection and configuration.

If your Palgate account is authorized to control more than one gate, you can select and configure any/all of them, one by one. You can also link other phones (accounts) to this integration, and configure the gates those phones are authorized for, the same way.

## Advanced Configuration
1. `Time (sec) gate takes to open` - The time it takes for the gate to open, in seconds (default 25)
2. `Time (sec) gate remains open` - The time the gate remains open, in seconds (default 45)
3. `Time (sec) gate takes to close` - The time it takes for the gate to close, in seconds (default 35)
4. `Allow triggering gate while opening, to invert direction` - If enabled, the gate can be triggered while opening, to invert the direction

## Features
### Cover
- Open
- Stop (in most gates, invert movement)
- Custom open/close timeouts
### Select Relay Mode
Using the Relay Mode selector entity (disabled by default), a user with the proper permissions can control the gate relay operational modes:
- Normal (open/close work as usual, per the other gate settings)
- Hold Open (gate opens and remains in the open position, disabling normal open/close control)
- Hold Close (gate closes and remains in the closed position, disabling normal open/close control)

This entity (new for v1.6 of this integration) is initially created as _disabled_. To use it, you will need to:
1. Explicitly enable the Relay Mode entity from the device page
2. Make sure the user (phone) that this gate is linked through, has the special permission for this action (on Palgate app, admin user: Gate settings -> Manager Options -> Users -> Selected user -> "Latch Output 1").\
➡️If the linked phone's user does not have the right permission, the selector entity will be marked `unavailable`. Once permission is granted, it will become operational.

At this time, this feature supports one output of the Palgate device - output1. This seems to cover most installations.

To use this in an automation, you can use the `select.select_option` action with the selector entity of the gate (e.g. `select.4G123456789_relay_mode`), available options: `normal`, `hold_open` and `hold_closed`.
### Actions (Services)
Starting with release 1.7.0, the integration exposes several actions, that can be used from scripts, automations or Developer Tools, to query / manage gate users, permissions and access log. For more information check out [ACTIONS](ACTIONS.md).
## Troubleshooting
### Secondary Device Not Authorized
You might encounter this error message when trying to perform a gate action (like open):
```
Failed to perform the action cover/open_cover. Not OK 400 {'err': 'not authorized', 'msg': 'Secondary device not authorized!', 'status': 'failed'}
```

This means your account is not allowed to use the `Linked Device` function for the gate you are trying to open.
To use it, ask the administrator of that gate to enable it, either globally for the gate or specifically for your user account.  
If you are the administrator (e.g. single gate / private home), you can do it via the Palgate App: Gate Settings -> Manager Options -> Users -> `your user` -> Linked Device.

For more details, see the Palgate tutorials: [Device linking](https://www.pal-es.com/tutorials?questionId=e9760d7e-fef3-4637-8cad-096940e2511e) | [User management](https://www.pal-es.com/tutorials?questionId=7af12cae-1854-4f55-93f6-f0f25391480b)

## Notes
- Palgate's API does not report the position of the gate. In practice, this means that Home Assistant does not have definitive knowledge of the gate being closed, being actively moving, or its current position. This in turn means that the indications of "opening", "closed" etc. are in fact simulated, based on your configured timing parameters (see [Advanced Configuration](#advanced-configuration) above).

## Note for Release 1.6.x

Release 1.6 introduces a new, _optional_ entity to the gate device. This new feature allows a user with the right permission to select between three gate operational modes: Normal, Hold Open and Hold Closed. See [Select Relay Mode](#select-relay-mode) above.

**Note**: Once you enable this entity, the integration will be polling the Palgate API server periodically for status. This is normal for HA integrations, but it is new for this version so worth mentioning.

Thanks to Matan for proposing this feature and providing valuable info.

## Note for Release 1.5.x

Release 1.5 brings a simplified and streamlined configuration process. You no longer need to manually look up and type your gate ID from the Palgate app - it is now fetched automatically. If your Palgate account is authorized for more than one gate, you will be presented with a list to choose from. One gate per configuration entry; configure as many as you need. Thanks to [adi6409](https://github.com/adi6409) for providing valuable info from his multi-gate setup.


## Note for Release 1.4.x

As of release 1.4 of this integration, each gate is set up as a separate device, with a single "cover" type control. In previous releases, if you added multiple gates, they were all created as multiple "cover" entities under one device. The new setup allows for better control of multiple gates, e.g. assigning them to different areas.

The entity names for the gates remain the same, so existing automations, scripts or scenes *should* continue functioning as before, but it is advised to double check that everything still works as planned.

## Administrivia - New Maintainer

As of 5 March 2026, I ([doron1](https://github.com/doron1)) will be taking over as maintainer of this repo. On behalf of the Palgate users' community I'd like to express deep gratitudes to [@ShonP40](https://github.com/ShonP40), who provided an excellent home and ongoing code maintainance to this integration for quite a few years, enabling the rest of us to control our home, community or municipal gates via Home Assistant.
## Credits
- [sindrebroch](https://github.com/sindrebroch) - Original creator
- [ShonP40](https://github.com/ShonP40) - Devoted owner/maintainer of this integration for many years
- [DonutByte](https://github.com/DonutByte) - [Python implementation with an updated time-sensitive token generator](https://github.com/DonutByte/pylgate)
- [bondar](https://github.com/bondar) - [Implemented support for devices that control multiple gates](https://github.com/doron1/ha-palgate/pull/18)
