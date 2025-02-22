#!/bin/bash

# Helper for generating a Palgate token inside the HA terminal shell.
# Requires Internet access from HA.
#
# @doron1 2025, v0.2

PACKAGE="git+https://github.com/DonutByte/pylgate.git@main"
SCRIPT="generate_linked_device_session_token.py"
SCRIPT_LOCATION="https://raw.githubusercontent.com/DonutByte/pylgate/refs/heads/main/examples"

Main () {

  trap Cleanup EXIT

  VENV_ACTIVATED=false
  TMPDIR=$(mktemp -dp . || FailWith "Unable to create temp dir")

  echo -e "\nPlease open the Palgate app on your phone, select \"Link Devices\" from the menu,"
  echo -e "and wait for the QR code to appear here, this may take a few moments."
  echo -e "When it appears, select \"Link A Device\" and scan the QR code.\n"
  echo -e "When done, copy the phone number, token and token type, you will need them when configuring the integration.\n"

  python3 -m venv $TMPDIR > /dev/null || FailWith "Unable to create Python venv"

  source $TMPDIR/bin/activate
  VENV_ACTIVATED=true

  # Bring in the good stuff from DonutByte
  pip3 -q install $PACKAGE > /dev/null || FailWith "Unable to install token generation program"
  wget -P $TMPDIR $SCRIPT_LOCATION/$SCRIPT > /dev/null 2>&1

  pip3 -q install qrcode requests > /dev/null

  python3 $TMPDIR/$SCRIPT

}

FailWith () {

  echo "Error: $*"
  exit 1

}

Cleanup () {

  echo "Cleaning up"
  $VENV_ACTIVATED && deactivate
  rm -fr $TMPDIR

}

Main $*