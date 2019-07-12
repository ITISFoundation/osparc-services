#!/bin/sh
#

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

# BOOTING application ---------------------------------------------
echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"

if [[ -v CREATE_DUMMY_TABLE ]]
then
    pushd /home/jovyan/scripts/dy_services_helpers; pip3 install -r requirements.txt; popd

    echo "Creating dummy tables ... using ${USE_CASE_CONFIG_FILE}"
    result="$(python3 /home/jovyan/scripts/dy_services_helpers/platform_initialiser.py ${USE_CASE_CONFIG_FILE} --folder ${TEST_DATA_PATH})";
    echo "Received result of $result";
    IFS=, read -a array <<< "$result";
    echo "Received result pipeline id of ${array[0]}";
    echo "Received result node uuid of ${array[1]}";
    # the fake SIMCORE_NODE_UUID is exported to be available to the service
    export SIMCORE_PROJECT_ID="${array[0]}";
    export SIMCORE_NODE_UUID="${array[1]}";
fi

if [[ ${SC_BUILD_TARGET} == "development" ]]
then
  echo "  Environment :"
  printenv  | sed 's/=/: /' | sed 's/^/    /' | sort
  #--------------------

elif [[ ${SC_BUILD_TARGET} == "production" ]]
then
  echo "Target is ${SC_BUILD_TARGET}"
fi


# start the dash-app now
python3 /home/jovyan/src/${APP_URL}
# gunicorn -b 0.0.0.0:8888 /home/jovyan/src/cc-rabbit-2d-simple:app