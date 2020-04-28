#!/bin/sh
# set sh strict mode
set -o errexit
set -o nounset
IFS=$(printf '\n\t')

cd /home/scu/opencorservice_demo

echo "starting service as"
echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"
echo "..."
echo
# ----------------------------------------------------------------
# This script shall be modified according to the needs in order to run the service
# The inputs defined in ${INPUT_FOLDER}/input.json are available as env variables by their key in capital letters
# For example: input_1 -> $INPUT_1

/home/opencor/OpenCOR-2019-06-11-Linux/bin/OpenCOR -c PythonRunScript::script /home/opencorservice_demo/run_model.py ${INPUT_FOLDER}/input.json /home/opencorservice_demo/guyton_antidiuretic_hormone_2008.cellml /home/opencorservice_demo/input_keymap.json

cp outputs.csv ${OUTPUT_FOLDER}/outputs.csv

env | grep INPUT