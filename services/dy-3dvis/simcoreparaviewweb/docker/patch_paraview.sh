#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'


# this allow the twisted based server to serve .rpy scripts:
# https://twisted.readthedocs.io/en/twisted-18.9.0/web/howto/web-in-60/rpy-scripts.html
sed -i '/^from twisted.web .*/a from twisted.web import script' /opt/paraview/lib/python2.7/site-packages/wslink/server.py
sed -i 's/^\(.*\)\(root = File(options.content).*$\)/\1root = File(options.content, ignoredExts=(".rpy",))\n\1root.processors = {".rpy": script.ResourceScript}/' /opt/paraview/lib/python2.7/site-packages/wslink/server.py