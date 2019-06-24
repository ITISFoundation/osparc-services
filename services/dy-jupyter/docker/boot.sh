#!/bin/bash

set -e

# BOOTING application ---------------------------------------------
echo "Booting application ..."
echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"


if test "${CREATE_DUMMY_TABLE}" = "1"
then
    pip install -r /home/jovyan/devel/requirements.txt
    pushd /home/jovyan/scripts/dy_services_helpers; pip3 install -r requirements.txt; popd

    echo "Creating dummy tables ... using ${USE_CASE_CONFIG_FILE}"
    result="$(python scripts/dy_services_helpers/platform_initialiser_csv_files.py ${USE_CASE_CONFIG_FILE} ${INIT_OPTIONS})"
    echo "Received result of $result";
    IFS=, read -a array <<< "$result";
    echo "Received result pipeline id of ${array[0]}";
    echo "Received result node uuid of ${array[1]}";
    # the fake SIMCORE_NODE_UUID is exported to be available to the service
    export SIMCORE_PROJECT_ID="${array[0]}";
    export SIMCORE_NODE_UUID="${array[1]}";
fi

# start the notebook now
echo "Setting theme ..."
jt -t grade3 -f ubuntu -fs 12 -T -N -cellw 90%
# start the notebook now
/docker/boot_notebook.sh
