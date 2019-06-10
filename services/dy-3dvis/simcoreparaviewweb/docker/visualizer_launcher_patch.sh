#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

sed -i -e '/"--authKey", "${secret}",/a "--settings-lod-threshold", "5", "--no-built-in-palette", "--color-palette-file", "/home/root/config/s4lColorMap.json",' /opt/wslink-launcher/launcher-template.json
#TODO: use an ENV here
if [ -d "/data/save-data" ] && [ -f "/data/save-data/state.pvsm" ]; then
    # modify launcher configuration
    sed -i -e '/"--authKey", "${secret}",/a "--load-file", "save-data/state.pvsm",' /opt/wslink-launcher/launcher-template.json
fi
