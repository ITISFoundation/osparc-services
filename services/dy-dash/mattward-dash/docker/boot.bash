#!/bin/bash
#

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

# BOOTING application ---------------------------------------------
echo "  User    :$(id "$(whoami)")"
echo "  Workdir :$(pwd)"

# shellcheck source=/dev/null
source "${VIRTUAL_VENV}"/bin/activate 

if [ -v CREATE_DUMMY_TABLE ]
then
    cd /home/jovyan/scripts/dy_services_helpers || exit 1; pip3 install -r requirements.txt; cd -

    echo "Creating dummy tables ... using ${USE_CASE_CONFIG_FILE}"
    result="$(python3 scripts/dy_services_helpers/platform_initialiser.py "${USE_CASE_CONFIG_FILE}" --folder '')";
    echo "Received result of $result";
    IFS=, read -r -a array <<< "$result";
    echo "Received result pipeline id of ${array[0]}";
    echo "Received result node uuid of ${array[1]}";
    # the fake SIMCORE_NODE_UUID is exported to be available to the service
    export SIMCORE_PROJECT_ID="${array[0]}";
    export SIMCORE_NODE_UUID="${array[1]}";
fi

if [ "${SC_BUILD_TARGET}" = "development" ]
then
  echo "  Environment :"
  printenv  | sed 's/=/: /' | sed 's/^/    /' | sort
  #--------------------

elif [ "${SC_BUILD_TARGET}" = "production" ]
then
  echo "Target is ${SC_BUILD_TARGET}"
fi


# start the dash-app now
python /home/jovyan/src/"${APP_URL}"