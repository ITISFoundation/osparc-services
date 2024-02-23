#!/bin/sh
#
# - Executes *inside* of the container upon start as --user [default root]
# - Notice that the container *starts* as --user [default root] but
#   *runs* as non-root user [scu]
#
set -o errexit
set -o nounset

IFS=$(printf '\n\t')

INFO="INFO: [$(basename "$0")] "
WARNING="WARNING: [$(basename "$0")] "
ERROR="ERROR: [$(basename "$0")] "

echo "$INFO" "Entrypoint for stage ${SC_BUILD_TARGET} ..."
echo "$INFO" "User :$(id "$(whoami)")"
echo "$INFO" "Workdir : $(pwd)"
echo "$INFO" "User : $(id scu)"
echo "$INFO" "python : $(command -v python)"
echo "$INFO" "pip : $(command -v pip)"

# expect input/output folders to be mounted
stat "${INPUT_FOLDER}" >/dev/null 2>&1 ||
    (echo "$ERROR" "You must mount '${INPUT_FOLDER}' to deduce user and group ids" && exit 1)
stat "${OUTPUT_FOLDER}" >/dev/null 2>&1 ||
    (echo "$ERROR" "You must mount '${OUTPUT_FOLDER}' to deduce user and group ids" && exit 1)

# NOTE: expects docker run ... -v /path/to/input/folder:${INPUT_FOLDER}
# check input/output folders are owned by the same user
if [ "$(stat -c %u "${INPUT_FOLDER}")" -ne "$(stat -c %u "${OUTPUT_FOLDER}")" ]; then
    echo "$ERROR" "'${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different user id's. not allowed" && exit 1
fi
# check input/outputfolders are owned by the same group
if [ "$(stat -c %g "${INPUT_FOLDER}")" -ne "$(stat -c %g "${OUTPUT_FOLDER}")" ]; then
    echo "$ERROR" "'${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different group id's. not allowed" && exit 1
fi

echo "$INFO" "setting correct user id/group id..."
HOST_USERID=$(stat --format=%u "${INPUT_FOLDER}")
HOST_GROUPID=$(stat --format=%g "${INPUT_FOLDER}")
CONT_GROUPNAME=$(getent group "${HOST_GROUPID}" | cut --delimiter=: --fields=1)
if [ "$HOST_USERID" -eq 0 ]; then
    echo "$WARNING" "Folder mounted owned by root user... adding $SC_USER_NAME to root..."
    adduser "$SC_USER_NAME" root
else
    echo "Folder mounted owned by user $HOST_USERID:$HOST_GROUPID-'$CONT_GROUPNAME'..."
    # take host's credentials in $SC_USER_NAME
    if [ -z "$CONT_GROUPNAME" ]; then
        echo "$INFO" "Creating new group my$SC_USER_NAME"
        CONT_GROUPNAME=my$SC_USER_NAME
        addgroup --gid "$HOST_GROUPID" "$CONT_GROUPNAME"
    else
        echo "$INFO" "group already exists"
    fi
    echo "$INFO" "adding $SC_USER_NAME to group $CONT_GROUPNAME..."
    adduser "$SC_USER_NAME" "$CONT_GROUPNAME"

    echo "$INFO" "changing $SC_USER_NAME:$SC_USER_NAME ($SC_USER_ID:$SC_USER_ID) to $SC_USER_NAME:$CONT_GROUPNAME ($HOST_USERID:$HOST_GROUPID)"
    usermod --uid "$HOST_USERID" --gid "$HOST_GROUPID" "$SC_USER_NAME"

    echo "$INFO" "Changing group properties of files around from $SC_USER_ID to group $CONT_GROUPNAME"
    find / \( -path /proc -o -path /sys \) -prune -o -group "$SC_USER_ID" -exec chgrp --no-dereference "$CONT_GROUPNAME" {} \;
    # change user property of files already around
    echo "$INFO" "Changing ownership properties of files around from $SC_USER_ID to group $CONT_GROUPNAME"
    find / \( -path /proc -o -path /sys \) -prune -o -user "$SC_USER_ID" -exec chown --no-dereference "$SC_USER_NAME" {} \;
fi

echo "$INFO" "Starting $* ..."
echo "$INFO" "  $SC_USER_NAME rights    : $(id "$SC_USER_NAME")"
echo "$INFO" "  local dir : $(ls -al)"
echo "$INFO" "  input dir : $(ls -al "${INPUT_FOLDER}")"
echo "$INFO" "  output dir : $(ls -al "${OUTPUT_FOLDER}")"

exec gosu "$SC_USER_NAME" "$@"
