#!/pyenv/versions/3.6.7/bin/python
# Note: this shebang is the one where the python 3.6 interpreter is installed by pyenv
import cgitb
cgitb.enable()
# this MUST come first

import asyncio

import logging
import os
from pathlib import Path
import time

from simcore_sdk.node_ports import exceptions
from simcore_sdk.node_data import data_manager

log = logging.getLogger(__name__)

# necessary for CGI scripting compatiblity
# https://docs.python.org/3/library/cgi.html
print("Content-Type: text/html;charset=utf-8")
print()

_STATE_PATH = os.environ.get("SIMCORE_NODE_APP_STATE_PATH", "undefined")

class StateHandler:
    @classmethod
    def _state_path(cls) -> Path:
        assert _STATE_PATH != "undefined", "SIMCORE_NODE_APP_STATE_PATH is not defined!"
        state_path = Path(_STATE_PATH)
        return state_path

    @classmethod
    async def post(cls):
        log.info("started pushing current state to S3...")
        print("pushing state")
        try:
            start_time = time.time()
            await data_manager.push(cls._state_path())
            end_time = time.time()
            print("time to push: {} seconds".format(end_time - start_time))
            print("Status: 204 No Contents")
        except exceptions.NodeportsException as exc:
            log.exception("Unexpected error while pushing state")
            print("Status: 500 {}".format(str(exc)))
    @classmethod
    async def get(cls):
        log.info("started pulling state to S3...")
        print("pulling state")
        try:
            start_time = time.time()
            await data_manager.pull(cls._state_path())
            end_time = time.time()
            print("time to pull: {} seconds".format(end_time - start_time))
            print("Status: 204 No Contents")
        except exceptions.S3InvalidPathError as exc:
            log.exception("Invalid path to S3 while retrieving state")
            print("Status: 404 {}".format(str(exc)))
        except exceptions.NodeportsException as exc:
            log.exception("Unexpected error while retrieving state")
            print("Status: 500 {}".format(str(exc)))

if __name__ == "__main__":
    request_method = os.environ["REQUEST_METHOD"]
    asyncio.get_event_loop().run_until_complete(getattr(StateHandler, request_method.lower())())
