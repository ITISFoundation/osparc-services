#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'
INFO="INFO: [$(basename "$0")] "

# BOOTING application ---------------------------------------------
echo "$INFO" "Starting container ..."
echo "$INFO" "  User    :$(id "$(whoami)")"
echo "$INFO" "  Workdir :$(pwd)"


# expect input/output folders to be mounted
stat "${DY_SIDECAR_PATH_INPUTS}" > /dev/null 2>&1 || \
        (echo "ERROR: You must mount '${DY_SIDECAR_PATH_INPUTS}' to deduce user and group ids" && exit 1)
stat "${DY_SIDECAR_PATH_OUTPUTS}" > /dev/null 2>&1 || \
    (echo "ERROR: You must mount '${DY_SIDECAR_PATH_OUTPUTS}' to deduce user and group ids" && exit 1)

# NOTE: expects docker run ... -v /path/to/input/folder:${DY_SIDECAR_PATH_INPUTS}
# check input/output folders are owned by the same user
if [ "$(stat -c %u "${DY_SIDECAR_PATH_INPUTS}")" -ne "$(stat -c %u "${DY_SIDECAR_PATH_OUTPUTS}")" ]
then
    echo "ERROR: '${DY_SIDECAR_PATH_INPUTS}' and '${DY_SIDECAR_PATH_OUTPUTS}' have different user id's. not allowed" && exit 1
fi
# check input/outputfolders are owned by the same group
if [ "$(stat -c %g "${DY_SIDECAR_PATH_INPUTS}")" -ne "$(stat -c %g "${DY_SIDECAR_PATH_OUTPUTS}")" ]
then
    echo "ERROR: '${DY_SIDECAR_PATH_INPUTS}' and '${DY_SIDECAR_PATH_OUTPUTS}' have different group id's. not allowed" && exit 1
fi

echo "listing inputs folder ${DY_SIDECAR_PATH_INPUTS}"
ls -lah "${DY_SIDECAR_PATH_INPUTS}"
echo "listing outputs folder ${DY_SIDECAR_PATH_OUTPUTS}"
ls -lah "${DY_SIDECAR_PATH_OUTPUTS}"

echo "setting correct user id/group id..."
HOST_USERID=$(stat -c %u "${DY_SIDECAR_PATH_INPUTS}")
HOST_GROUPID=$(stat -c %g "${DY_SIDECAR_PATH_INPUTS}")
CONTAINER_GROUPNAME=$(getent group | grep "${HOST_GROUPID}" | cut --delimiter=: --fields=1 || echo "")
echo "CONTAINER_GROUPNAME='$CONTAINER_GROUPNAME'"

if [ "$HOST_USERID" -eq 0 ]
then
    echo "Warning: Folder mounted owned by root user... adding $SC_USER_NAME to root..."
    addgroup "$SC_USER_NAME" root
else
    echo "Folder mounted owned by user $HOST_USERID:$HOST_GROUPID-'$CONTAINER_GROUPNAME'..."
    # take host's credentials in $SC_USER_NAME
    if [ -z "$CONTAINER_GROUPNAME" ]
    then
        echo "Creating new group my$SC_USER_NAME"
        CONTAINER_GROUPNAME=my$SC_USER_NAME
        addgroup --gid "$HOST_GROUPID" "$CONTAINER_GROUPNAME"
    else
        echo "group already exists"
    fi

    echo "adding $SC_USER_NAME to group $CONTAINER_GROUPNAME..."
    usermod --append --groups "$CONTAINER_GROUPNAME" "$SC_USER_NAME" 
    
    echo "Changing owner ship of state directory /home/${SC_USER_NAME}/work/workspace"
    chown --recursive "$SC_USER_NAME" "/home/${SC_USER_NAME}/work/workspace"
    echo "Changing owner ship of state directory ${DY_SIDECAR_PATH_INPUTS}"
    chown --recursive "$SC_USER_NAME" "${DY_SIDECAR_PATH_INPUTS}"
    echo "Changing owner ship of state directory ${DY_SIDECAR_PATH_OUTPUTS}"
    chown --recursive "$SC_USER_NAME" "${DY_SIDECAR_PATH_OUTPUTS}"
fi

#su --command "export PATH=${PATH}:/home/$SC_USER_NAME/service.cli; $*" "$SC_USER_NAME"
exec gosu "$SC_USER_NAME" /home/$SC_USER_NAME/service.cli/execute.sh
