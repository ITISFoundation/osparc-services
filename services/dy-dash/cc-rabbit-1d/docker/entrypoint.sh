#!/bin/sh
set -e
# This entrypoint script:
#
# - Executes *inside* of the container upon start as --user [default root]
# - Notice that the container *starts* as --user [default root] but
#   *runs* as non-root user [$SC_USER_NAME]
#
echo "Entrypoint for stage ${SC_BUILD_TARGET} ..."
echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"


# expect input/output/log folders to be mounted
stat $INPUT_FOLDER &> /dev/null || \
        (echo "ERROR: You must mount '$INPUT_FOLDER' to deduce user and group ids" && exit 1)
stat $OUTPUT_FOLDER &> /dev/null || \
    (echo "ERROR: You must mount '$OUTPUT_FOLDER' to deduce user and group ids" && exit 1)
stat $LOG_FOLDER &> /dev/null || \
    (echo "ERROR: You must mount '$LOG_FOLDER' to deduce user and group ids" && exit 1)

# NOTE: expects docker run ... -v /path/to/input/folder:$INPUT_FOLDER
# check input/output/log folders are owned by the same user
if [[ $(stat -c %u $INPUT_FOLDER) -ne $(stat -c %u $OUTPUT_FOLDER) ]]
then
    (echo "ERROR: '$INPUT_FOLDER' and '$OUTPUT_FOLDER' have different user id's. not allowed" && exit 1)
elif [[ $(stat -c %u $INPUT_FOLDER) -ne $(stat -c %u $LOG_FOLDER) ]]
then
    (echo "ERROR: '$INPUT_FOLDER' and '$LOG_FOLDER' have different user id's. not allowed" && exit 1)
fi
# check input/output/log folders are owned by the same group
if [[ $(stat -c %g $INPUT_FOLDER) -ne $(stat -c %g $OUTPUT_FOLDER) ]]
then
    (echo "ERROR: '$INPUT_FOLDER' and '$OUTPUT_FOLDER' have different group id's. not allowed" && exit 1)
elif [[ $(stat -c %g $INPUT_FOLDER) -ne $(stat -c %g $LOG_FOLDER) ]]
then
    (echo "ERROR: '$INPUT_FOLDER' and '$LOG_FOLDER' have different group id's. not allowed" && exit 1)
fi

USERID=$(stat -c %u $INPUT_FOLDER)
GROUPID=$(stat -c %g $INPUT_FOLDER)
GROUPNAME=$(getent group ${GROUPID} | cut -d: -f1)
if [[ $USERID -eq 0 ]]
then
    echo "Warning: Folder mounted owned by root user... adding $SC_USER_NAME to root..."
    addgroup $SC_USER_NAME root
else
    echo "Folder mounted owned by user $USERID:$GROUPID-'$GROUPNAME'..."
    # take host's credentials in $SC_USER_NAME
    if [[ -z "$GROUPNAME" ]]
    then
        echo "Creating new group my$SC_USER_NAME"
        GROUPNAME=my$SC_USER_NAME
        addgroup -g $GROUPID $GROUPNAME
        # change group property of files already around
        find / -group $SC_USER_ID -exec chgrp -h $GROUPNAME {} \;
    else
        echo "adding $SC_USER_NAME to group $GROUPNAME..."
        addgroup $SC_USER_NAME $GROUPNAME
    fi

    echo "changing $SC_USER_NAME $SC_USER_ID:$SC_USER_ID to $USERID:$GROUPID"
    deluser $SC_USER_NAME &> /dev/null
    if [[ "$SC_USER_NAME" == "$GROUPNAME" ]]
    then
        addgroup -g $GROUPID $GROUPNAME
    fi
    adduser -u $USERID -G $GROUPNAME -D -s /bin/sh $SC_USER_NAME
    # change user property of files already around
    find / -user $SC_USER_ID -exec chown -h $SC_USER_NAME {} \;
fi




# Appends docker group if socket is mounted
DOCKER_MOUNT=/var/run/docker.sock

if [[ -e $DOCKER_MOUNT && stat $DOCKER_MOUNT &> /dev/null && $? -eq 0 ]]
then
    GROUPID=$(stat -c %g $DOCKER_MOUNT)
    
    GROUPNAME=scdocker

    addgroup -g $GROUPID $GROUPNAME &> /dev/null
    if [[ $? -gt 0 ]]
    then
        # if group already exists in container, then reuse name
        GROUPNAME=$(getent group ${GROUPID} | cut -d: -f1)
    fi
    addgroup $SC_USER_NAME $GROUPNAME
fi

echo "Starting $@ ..."
echo "  $SC_USER_NAME rights    :`id $SC_USER_NAME`"
echo "  local dir :`ls -al`"
echo "  input dir :`ls -al $INPUT_FOLDER`"
echo "  output dir :`ls -al $OUTPUT_FOLDER`"
echo "  log dir :`ls -al $LOG_FOLDER`"

su-exec $SC_USER_NAME "$@"
