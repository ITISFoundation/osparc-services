import asyncio
import json
import logging

import input_retriever
from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join

logger = logging.getLogger(__name__)


class RetrieveHandler(IPythonHandler):
    def initialize(self): #pylint: disable=no-self-use
        input_retriever.init()

    # deprecated: get download everything and upload everything
    async def get(self):
        try:
            results = await asyncio.gather(
                input_retriever.download_data(port_keys=[]),
                input_retriever.upload_data(port_keys=[]))
            transfered_size = sum(results)
            self.write(json.dumps({
                "data": {
                    "size_bytes": transfered_size
                }
            }))
            self.set_status(200)
        except Exception as exc: #pylint: disable=broad-except
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500, reason=str(exc))
        finally:
            self.finish('completed retrieve!')

    async def post(self):
        request_contents = json.loads(self.request.body)
        ports = request_contents["port_keys"]
        logger.info("getting data of ports %s from previous node with POST request...", ports)
        try:
            transfered_size = await input_retriever.download_data(ports)
            self.write(json.dumps({
                "data": {
                    "size_bytes": transfered_size
                }
            }))
            self.set_status(200)
        except Exception as exc: #pylint: disable=broad-except
            logger.exception("Unexpected problem when processing retrieve call")
            self.set_status(500, reason=str(exc))
        finally:
            self.finish()

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
