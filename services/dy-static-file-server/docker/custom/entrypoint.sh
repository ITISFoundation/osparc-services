#!/bin/sh
set -o errexit
set -o nounset

IFS=$(printf '\n\t')
# This entrypoint script:
#
# - Executes *inside* of the container upon start as --user [default root]
# - Notice that the container *starts* as --user [default root] but
#   *runs* as non-root user [$SC_USER_NAME]
#
echo Entrypoint for stage "${SC_BUILD_TARGET}" ...
echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"


# adapt to be compatible for legacy boot mode
if [ -n "$SIMCORE_NODE_BASEPATH" ]; then
    echo "Boot mode: LEGACY"
    echo "Creating ${INPUT_FOLDER} and ${OUTPUT_FOLDER}"
    mkdir -p "${INPUT_FOLDER}"
    mkdir -p "${OUTPUT_FOLDER}"
    echo "SERVER_ROOT: ${SERVER_ROOT}"
    echo "SIMCORE_NODE_BASEPATH: ${SIMCORE_NODE_BASEPATH}"
    echo "Creating ${SERVER_ROOT}${SIMCORE_NODE_BASEPATH} and changin ownership to $SC_USER_NAME"
    mkdir -p "${SERVER_ROOT}${SIMCORE_NODE_BASEPATH}"
    chown -R "$SC_USER_NAME" "${SERVER_ROOT}${SIMCORE_NODE_BASEPATH}"
else 
    echo "Boot mode: DYNAMIC-SIDECAR"
fi


# expect input/output folders to be mounted
#TODO: determine if legacy boot more and based on that do stuff like creating 
stat "${INPUT_FOLDER}" > /dev/null 2>&1 || \
        (echo "ERROR: You must mount '${INPUT_FOLDER}' to deduce user and group ids" && exit 1)
stat "${OUTPUT_FOLDER}" > /dev/null 2>&1 || \
    (echo "ERROR: You must mount '${OUTPUT_FOLDER}' to deduce user and group ids" && exit 1)

# NOTE: expects docker run ... -v /path/to/input/folder:${INPUT_FOLDER}
# check input/output folders are owned by the same user
if [ "$(stat -c %u "${INPUT_FOLDER}")" -ne "$(stat -c %u "${OUTPUT_FOLDER}")" ]
then
    echo "ERROR: '${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different user id's. not allowed" && exit 1
fi
# check input/outputfolders are owned by the same group
if [ "$(stat -c %g "${INPUT_FOLDER}")" -ne "$(stat -c %g "${OUTPUT_FOLDER}")" ]
then
    echo "ERROR: '${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different group id's. not allowed" && exit 1
fi

echo "listing inputs folder"
ls -lah "${INPUT_FOLDER}"
echo "listing outputs folder"
ls -lah "${OUTPUT_FOLDER}"

echo "setting correct user id/group id..."
HOST_USERID=$(stat -c %u "${INPUT_FOLDER}")
HOST_GROUPID=$(stat -c %g "${INPUT_FOLDER}")
CONT_GROUPNAME=$(getent group "${HOST_GROUPID}" | cut -d: -f1)
if [ "$HOST_USERID" -eq 0 ]
then
    echo "Warning: Folder mounted owned by root user... adding $SC_USER_NAME to root..."
    addgroup "$SC_USER_NAME" root
else
    echo "Folder mounted owned by user $HOST_USERID:$HOST_GROUPID-'$CONT_GROUPNAME'..."
    # take host's credentials in $SC_USER_NAME
    if [ -z "$CONT_GROUPNAME" ]
    then
        echo "Creating new group my$SC_USER_NAME"
        CONT_GROUPNAME=my$SC_USER_NAME
        addgroup -g "$HOST_GROUPID" "$CONT_GROUPNAME"
    else
        echo "group already exists"
    fi

    echo "changing $SC_USER_NAME $SC_USER_ID:$SC_USER_ID to $HOST_USERID:$HOST_GROUPID"
    # in alpine there is no such thing as usermod... so we delete the user and re-create it as part of $CONT_GROUPNAME
    deluser "$SC_USER_NAME" > /dev/null 2>&1
    adduser -u "$HOST_USERID" -G "$CONT_GROUPNAME" -D -s /bin/sh "$SC_USER_NAME"

    echo "Changing group properties of files around from $SC_USER_ID to group $CONT_GROUPNAME"
    find / -path /var/log/nginx -prune -o -group "$SC_USER_ID" -print
    find / -path /var/log/nginx -prune -o -group "$SC_USER_ID" -exec chgrp -h "$CONT_GROUPNAME" {} \;
    # change user property of files already around
    echo "Changing ownership properties of files around from $SC_USER_ID to group $CONT_GROUPNAME"
    find / -path /var/log/nginx -prune -o -user "$SC_USER_ID" -exec chown -h "$SC_USER_NAME" {} \;
    find / -path /var/log/nginx -prune -o -user "$SC_USER_ID" -print
fi

echo "Starting $* ..."
echo "  $SC_USER_NAME rights    : $(id "$SC_USER_NAME")"
echo "  local dir : $(ls -al)"
echo "  input dir : $(ls -al "${INPUT_FOLDER}")"
echo "  output dir : $(ls -al "${OUTPUT_FOLDER}")"


# from original etrypoint
set -e

# Check if incomming command contains flags.
if [ "${1#-}" != "$1" ]; then
    set -- static-web-server "$@"
fi

su-exec "$SC_USER_NAME" "$@"
