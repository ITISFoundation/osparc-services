#! /bin/sh
set -o errexit
# set -o nounset

IFS=$(printf '\n\t')

echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"
echo   Env      : "$(env)"

echo "/workdir content"
ls -lah

echo "ensure some random data is created in /workdir/generated-data content"
python3 ensure_random_workdir_data.py

echo "/workdir/generated-data content"
ls -lah /workdir/generated-data/

echo "starting background inputs->ouputs mapping when inputs change"
python3 inputs_to_outputs.py &

echo "booting static-web-server"
exec static-web-server