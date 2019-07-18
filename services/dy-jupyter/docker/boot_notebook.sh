#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

# try to pull data from S3
echo
echo "trying to restore state..."
python /docker/state_puller.py ${SIMCORE_NODE_APP_STATE_PATH} --silent

# the notebooks in the folder shall be trusted by default
# jupyter trust ${SIMCORE_NODE_APP_STATE_PATH}/*

# Trust all notebooks in the notbooks folder
echo
echo "trust all notebooks in path..."
find ${SIMCORE_NODE_APP_STATE_PATH} -name '*.ipynb' | xargs jupyter trust

# prevents notebook to open in separate tab
cat > ~/.jupyter/custom/custom.js <<EOF
define(['base/js/namespace'], function(Jupyter){
    Jupyter._target = '_self';
});
EOF

#https://github.com/jupyter/notebook/issues/3130 for delete_to_trash
#https://github.com/nteract/hydrogen/issues/922 for disable_xsrf
cat > jupyter_config.json <<EOF
{
    "NotebookApp": {
        "ip": "0.0.0.0",
        "port": 8888,
        "base_url": "${SIMCORE_NODE_BASEPATH}",
        "extra_static_paths": ["${SIMCORE_NODE_BASEPATH}/static"],
        "notebook_dir": "${SIMCORE_NODE_APP_STATE_PATH}",
        "token": "",
        "quit_button": false,
        "open_browser": false,
        "webbrowser_open_new": 0,
        "disable_check_xsrf": true,
        "nbserver_extensions": {
            "retrieve": true,
            "push": true,
            "state_handler": true
        }
    },
    "FileContentsManager": {
        "post_save_hook": "post_save_hook.export_to_osparc_hook",
        "delete_to_trash": false
    },
    "Session": {
        "debug": false
    }
}
EOF

# call the notebook with the basic parameters
start-notebook.sh --config jupyter_config.json "$@"
