#!/bin/sh
# set sh strict mode
set -o errexit
set -o nounset
IFS=$(printf '\n\t')

cd ~/pmr_mrg

echo "starting service as"
echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"
echo "..."
echo
# ----------------------------------------------------------------
# This script shall be modified according to the needs in order to run the service
# The inputs defined in ${INPUT_FOLDER}/inputs.json are available as env variables by their key in capital letters
# For example: input_1 -> $INPUT_1

/home/opencor/OpenCOR-2020-02-14-Linux/pythonshell /home/pmr_mrg/run_model_2020.py ${INPUT_FOLDER}/inputs.json /home/pmr_mrg/mcintyre_richardson_grill_model_2001.cellml /home/pmr_mrg/input_keymap.json

cp outputs.csv ${OUTPUT_FOLDER}/outputs.csv

env | grep INPUT