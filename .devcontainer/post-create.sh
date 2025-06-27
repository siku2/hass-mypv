#!/usr/bin/env bash
set -euo pipefail

_HA_VERSION=$(jq -r '.homeassistant' hacs.json)

python3 -m pip install colorlog "homeassistant==$_HA_VERSION" zlib_ng
