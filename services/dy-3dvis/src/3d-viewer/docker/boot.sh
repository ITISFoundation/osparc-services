#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

echo
echo "current directory is ${PWD}"

echo
echo "set up python 3"
export PATH="${PYENV_ROOT}/bin:$PATH"
eval "$(pyenv init -)"
python -V
pip -V

if [[ -v CREATE_DUMMY_TABLE ]];
then
    pushd /home/root/scripts/dy_services_helpers; pip3 install -r requirements.txt; popd
    # in dev mode, data located in mounted volume /test-data are uploaded to the S3 server
    # also a fake configuration is set in the DB to simulate the osparc platform
    echo
    echo "development mode, init dummy pipeline..."
    # in style: pipelineid,nodeuuid
    result="$(python3 scripts/dy_services_helpers/platform_initialiser.py ${USE_CASE_CONFIG_FILE} --folder ${TEST_DATA_PATH})";
    echo "Received result of $result";
    IFS=, read -ra array <<< "$result";
    echo "Received result pipeline id of ${array[0]}";
    echo "Received result node uuid of ${array[1]}";
    # the fake SIMCORE_NODE_UUID is exported to be available to the service
    export SIMCORE_NODE_UUID="${array[1]}";
    export SIMCORE_PROJECT_ID="${array[0]}"
    # we need to copy the handlers in the correct folder (only for debug mode to prevent masking files)
    cp handlers/*.rpy /opt/paraview/share/paraview-5.6/web/visualizer/www/
fi

# try to pull data from S3
echo
echo "trying to download previous state..."
python docker/state_manager.py pull --path "${SIMCORE_NODE_APP_STATE_PATH}" --silent
echo "...DONE"
echo

# patch paraview
echo
echo "patching paraviewweb to allow for rpy scripts to run..."
docker/patch_paraview.sh

# set default parameters (note that port is the server local port, and host is used for the websocket location)
echo
echo "setting up visualizer options..."
visualizer_options=(--content /opt/paraview/share/paraview-5.6/web/visualizer/www/ \
                    --data "${PARAVIEW_INPUT_PATH}" \
                    # --host localhost:80"${SIMCORE_NODE_BASEPATH}" \
                    --port "${SERVER_PORT}" \
                    # --ws-endpoint ${SIMCORE_NODE_BASEPATH}/ws \
                    --timeout 20000 \
                    --no-built-in-palette \
                    --color-palette-file /home/root/config/s4lColorMap.json \
                    --settings-lod-threshold 5 \
                    )

# set auto load state if available
if [ -f "${PARAVIEW_INPUT_PATH}/${SIMCORE_STATE_FILE}" ]; then
    echo
    echo "setting autoload of ${SIMCORE_STATE_FILE}"
    visualizer_options+=(--load-file "${SIMCORE_STATE_FILE}")
fi

# show additional debugging parameters on demand
if [[ ${PARAVIEW_DEBUG} != 0 ]]; then
    echo
    echo "setting paraview debug mode on"
    visualizer_options+=(--debug)
fi

# start server
echo
echo "starting paraview on ${SIMCORE_HOST_NAME}${SIMCORE_NODE_BASEPATH}..."
echo "using " "${visualizer_options[@]}"
/opt/paraview/bin/pvpython -dr --mpi \
    /opt/paraview/share/paraview-5.6/web/visualizer/server/pvw-visualizer.py "${visualizer_options[@]}"
