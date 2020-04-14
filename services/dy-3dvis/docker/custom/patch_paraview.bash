#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'


# this allow the twisted based server to serve .rpy scripts:
# https://twisted.readthedocs.io/en/twisted-18.9.0/web/howto/web-in-60/rpy-scripts.html
sed -i '/^from twisted.web .*/a from twisted.web import script' /opt/paraview/lib/python2.7/site-packages/wslink/server.py
sed -i 's/^\(.*\)\(root = File(options.content).*$\)/\1root = File(options.content, ignoredExts=(".rpy",))\n\1root.processors = {".rpy": script.ResourceScript}/' /opt/paraview/lib/python2.7/site-packages/wslink/server.py

# patch visualizer.js to ensure the websocket connection path is correct from the client behind the reverse proxy (e.g. will be something like https://osparc.io/x/12345/ws)
sed -i 's|"/ws"|"'"${SIMCORE_NODE_BASEPATH}"'/ws"|' /opt/paraview/share/paraview-5.6/web/visualizer/www/Visualizer.js
# patch visualizer.js to ensure the websocket connection path is using the correct protocol
sed -i 's|"https"===window.location.protocol|window.location.protocol.startsWith("https")|' /opt/paraview/share/paraview-5.6/web/visualizer/www/Visualizer.js
# patch visualizer.js to ensure the location of that endpoint is correct from the client behind the reverse proxy
sed -i 's|"/paraview/"|"'"${SIMCORE_NODE_BASEPATH}"'/paraview/"|' /opt/paraview/share/paraview-5.6/web/visualizer/www/Visualizer.js
