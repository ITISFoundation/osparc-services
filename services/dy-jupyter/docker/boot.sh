#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

# BOOTING application ---------------------------------------------
echo "Booting application ..."
echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"


if [ -v CREATE_DUMMY_TABLE ] && [ "${CREATE_DUMMY_TABLE}" = "1" ]
then
    pip install -r /home/jovyan/devel/requirements.txt
    pushd /home/jovyan/scripts/dy_services_helpers; pip install -r requirements.txt; popd

    echo "Creating dummy tables ... using ${USE_CASE_CONFIG_FILE}"
    result="$(python scripts/dy_services_helpers/platform_initialiser.py "${USE_CASE_CONFIG_FILE}" --folder "${TEST_DATA_PATH}")"
    echo "Received result of $result";
    IFS=, read -ra array <<< "$result";
    echo "Received result pipeline id of ${array[0]}";
    echo "Received result node uuid of ${array[1]}";
    # the fake SIMCORE_NODE_UUID is exported to be available to the service
    export SIMCORE_PROJECT_ID="${array[0]}";
    export SIMCORE_NODE_UUID="${array[1]}";
fi

# start the notebook now
echo
echo "Setting theme ..."
jt -t grade3 -f ubuntu -fs 12 -T -N -cellw 90%
# start the notebook now
echo
echo "Starting notebook ..."
/docker/boot_notebook.sh
