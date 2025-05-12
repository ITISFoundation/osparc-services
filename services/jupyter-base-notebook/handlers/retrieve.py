import asyncio
import json
import logging

from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join

logger = logging.getLogger(__name__)


class RetrieveHandler(IPythonHandler):
    # deprecated: get download everything and upload everything
    async def get(self):
        pass
    async def post(self):
        pass

def load_jupyter_server_extension(nb_server_app):
    """ Called when the extension is loaded

    - Adds API to server

    :param nb_server_app: handle to the Notebook webserver instance.
    :type nb_server_app: NotebookWebApplication
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/retrieve')

    web_app.add_handlers(host_pattern, [(route_pattern, RetrieveHandler)])
