#!/bin/bash

set -e

# BOOTING application ---------------------------------------------
echo "Booting application ..."
echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"

# start the notebook now
echo "Setting theme ..."
jt -t grade3 -f ubuntu -fs 12 -T -N -cellw 90%
/docker/boot_notebook.sh
