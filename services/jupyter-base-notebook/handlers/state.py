import logging
import os
from pathlib import Path

from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join

log = logging.getLogger(__name__)

_STATE_PATH = os.environ.get("SIMCORE_NODE_APP_STATE_PATH", "undefined")

def _state_path() -> Path:
    assert _STATE_PATH != "undefined", "SIMCORE_NODE_APP_STATE_PATH is not defined!"
    state_path = Path(_STATE_PATH)
    return state_path

class StateHandler(IPythonHandler):
    def initialize(self): #pylint: disable=no-self-use
        pass

    async def post(self):
        pass

    async def get(self):
        pass

def load_jupyter_server_extension(nb_server_app):
    """ Called when the extension is loaded

    - Adds API to server

    :param nb_server_app: handle to the Notebook webserver instance.
    :type nb_server_app: NotebookWebApplication
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/state')

    web_app.add_handlers(host_pattern, [(route_pattern, StateHandler)])
