#!/bin/sh
#
set -e

# BOOTING application ---------------------------------------------
echo "Booting in ${SC_BOOT_MODE} mode ..."
echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"


if [[ ${SC_BUILD_TARGET} == "development" ]]
then
  echo "  Environment :"
  printenv  | sed 's/=/: /' | sed 's/^/    /' | sort
  #--------------------

elif [[ ${SC_BUILD_TARGET} == "production" ]]
then
  echo "Target is ${SC_BUILD_TARGET}"
fi


# RUNNING application ----------------------------------------
if [[ ${BOOT_MODE} == "debug" ]]
then
  echo "debuging..."
else
  echo "running in release mode..."
fi

/bin/sh