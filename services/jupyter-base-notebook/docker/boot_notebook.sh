#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

echo
echo "current directory is ${PWD}"

# create output folder
echo
echo "creating inputs/outputs folder"
mkdir -p "${INPUTS_FOLDER}" # must match dy-sidecar state-paths-whatever
mkdir -p "${OUTPUTS_FOLDER}" # must match dy-sidecar state-paths-whatever

# the notebooks in the folder shall be trusted by default
# jupyter trust ${SIMCORE_NODE_APP_STATE_PATH}/*

# Trust all notebooks in the notbooks folder
echo
echo "trust all notebooks in path..."
find "/home/jovyan/notebooks" -name '*.ipynb' -exec jupyter trust {} \;

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
        "notebook_dir": "/home/jovyan/notebooks",
        "token": "",
        "quit_button": false,
        "open_browser": false,
        "webbrowser_open_new": 0,
        "disable_check_xsrf": true
    },
    "FileContentsManager": {
    },
    "Session": {
        "debug": false
    }
}
EOF

# call the notebook with the basic parameters
start-notebook.sh --config jupyter_config.json "$@"
