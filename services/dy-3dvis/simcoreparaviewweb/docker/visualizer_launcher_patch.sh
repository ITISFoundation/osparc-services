#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

sed -i -e '/"--authKey", "${secret}",/a "--settings-lod-threshold", "5", "--no-built-in-palette", "--color-palette-file", "/home/root/config/s4lColorMap.json",' /opt/wslink-launcher/launcher-template.json
