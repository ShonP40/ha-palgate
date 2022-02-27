# Palgate for HomeAssistant

![GitHub release (latest by date)](https://img.shields.io/github/v/release/sindrebroch/ha-palgate?style=flat-square)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

HomeAssistant-integration for Palgate

Unofficial integration, use at your own risk

## Requirements
You need to sniff your token from the app, this integration does a simple REST-command to open a gate by ID with your token in the header.

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Add this repository as a custom repository
3. Search for and install the "Palgate"-integration.
4. Restart Home Assistant.
5. Configure the `Palgate` integration.

### MANUAL INSTALLATION

1. Download the `Source code (zip)` file from the
   [latest release](https://github.com/sindrebroch/ha-palgate/releases/latest).
2. Unpack the release and copy the `custom_components/ha-palgate` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Restart Home Assistant.
4. Configure the `Palgate`-integration.

## Todo
- [ ] Add ability to customize open- and close-timeouts

## Features
### Cover
Open

- Close cover does not do anything
- Cover does not report position, and the state is assumed. This is because there is no API for polling the state.
