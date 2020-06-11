#!/bin/sh
# set sh strict mode
set -o errexit
set -o nounset
IFS=$(printf '\n\t')

cd $OUTPUT_FOLDER/

echo "starting service as"
echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"
echo "..."
echo
# ----------------------------------------------------------------
# This script shall be modified according to the needs in order to run the service
# The inputs defined in ${INPUT_FOLDER}/inputs.json are available as env variables by their key in capital letters
# For example: input_1 -> $INPUT_1

echo "Starting simulation..."
/home/scu/cardiac_myocyte_grandi/run_cardiac_myocyte_grandi.sh /usr/local/MATLAB/MATLAB_Runtime/v97/ ${INPUT_000} ${INPUT_001} ${INPUT_002} ${INPUT_003}
echo "Simulation finished!"

