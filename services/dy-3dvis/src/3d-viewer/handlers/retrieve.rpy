import json
import logging
from subprocess import PIPE, Popen

from twisted.web.resource import Resource

log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)

PYTHON3_BIN = "/pyenv/versions/3.6.7/bin/python"
PYTHON3_CMD = "/home/root/utils/input-retriever.py"


def call_python3(cmd, request):
    cmd = "{} {}".format(PYTHON3_BIN, cmd)
    process = Popen(cmd, stdout=PIPE, shell=True)
    output, err = process.communicate()
    log.info(output)
    if process.returncode != 0:
        request.setResponseCode(500, message=str(err))
        return "FAILURE".encode('utf-8')

    request.setResponseCode(200)
    request.setHeader("Content-Type", "application/json")
    return json.dumps(
        {
            "data": {
                "size_bytes": output
            }
        }
    ).encode('utf-8')

    # return output.encode('utf-8')


class MyResource(Resource):
    def render_GET(self, request):
        log.info("getting data from previous node...")
        cmd = "/home/root/utils/input-retriever.py"
        return call_python3(cmd, request)

    def render_POST(self, request):
        request_contents = json.loads(request.content.getvalue())
        ports = request_contents["port_keys"]
        log.info(
            "getting data of ports %s from previous node with POST request...", ports)
        cmd = "/home/root/utils/input-retriever.py --port_keys {}".format(
            " ".join(ports))
        return call_python3(cmd, request)


resource = MyResource()
