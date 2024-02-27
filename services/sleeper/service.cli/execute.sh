#!/bin/sh
# set sh strict mode
set -o errexit
set -o nounset
IFS=$(printf '\n\t')

cd /home/scu/sleeper

echo "starting service as"
echo "User    : $(id "$(whoami)")"
echo "Workdir : $(pwd)"
echo "..."
echo

python3 main.py
