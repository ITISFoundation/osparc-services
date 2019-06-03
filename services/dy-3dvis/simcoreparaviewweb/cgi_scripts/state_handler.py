#!/pyenv/versions/3.6.7/bin/python
# Note: this shebang is the one where the python 3.6 interpreter is installed by pyenv
import cgitb
cgitb.enable()
# this MUST come first

# import asyncio

# import logging
import os
# from pathlib import Path

# from simcore_sdk.node_ports import exceptions
# from simcore_sdk.node_data import data_manager

# log = logging.getLogger(__name__)

# necessary for CGI scripting compatiblity
# https://docs.python.org/3/library/cgi.html
print("Content-Type: text/html;charset=utf-8")
print()
print(os.environ)

_STATE_PATH = os.environ.get("SIMCORE_NODE_APP_STATE_PATH", "undefined")

# def _state_path() -> Path:
#     assert _STATE_PATH != "undefined", "SIMCORE_NODE_APP_STATE_PATH is not defined!"
#     state_path = Path(_STATE_PATH)
#     return state_path

# async def post(self):
#     log.info("started pushing current state to S3...")
#     try:
#         await data_manager.push(_state_path())
#         self.set_status(204)
#     except exceptions.NodeportsException as exc:
#         log.exception("Unexpected error while pushing state")
#         self.set_status(500, reason=str(exc))
#     finally:
#         self.finish()

# async def get(self):
#     log.info("started pulling state to S3...")
#     try:
#         await data_manager.pull(_state_path())
#         self.set_status(204)
#     except exceptions.S3InvalidPathError as exc:
#         log.exception("Invalid path to S3 while retrieving state")
#         self.set_status(404, reason=str(exc))
#     except exceptions.NodeportsException as exc:
#         log.exception("Unexpected error while retrieving state")
#         self.set_status(500, reason=str(exc))
#     finally:
#         self.finish('completed pulling state')

