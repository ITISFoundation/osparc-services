#! /bin/sh
set -o errexit
# set -o nounset

IFS=$(printf '\n\t')

echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"
echo   Env      : "$(env)"


if [ -n "${SIMCORE_NODE_BASEPATH+set}" ]
then
    echo
    echo moving website to "${NGINX_SERVER_ROOT}${SIMCORE_NODE_BASEPATH}"...
    echo

    mkdir -p "${NGINX_SERVER_ROOT}${SIMCORE_NODE_BASEPATH}"
    mv "${NGINX_SERVER_ROOT}"/*.txt "${NGINX_SERVER_ROOT}${SIMCORE_NODE_BASEPATH}"

    echo "Nginx will serve from ${NGINX_SERVER_ROOT}${SIMCORE_NODE_BASEPATH}"
    
else
    echo "Nginx will serve from ${NGINX_SERVER_ROOT}, nothing to do"
fi

# ensure some random data is created in /workdir
/venv/bin/python ensure_random_workdir_data.py

# keep mirroring running in the background
exec /venv/bin/python folder_mirror.py &
exec nginx -g "daemon off;" 