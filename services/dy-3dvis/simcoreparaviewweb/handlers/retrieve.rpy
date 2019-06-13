import logging
from twisted.web.resource import Resource
from subprocess import Popen, PIPE

log = logging.getLogger(__file__)

PYTHON3_BIN = "/pyenv/versions/3.6.7/bin/python"
PYTHON3_CMD = "/home/root/docker/input-retriever.py"


def call_python3(cmd, request):
    cmd = "{} {}".format(PYTHON3_BIN, cmd)
    process = Popen(cmd, stdout=PIPE, shell=True)
    output, err = process.communicate()
    log.info(output)
    if process.returncode != 0:
        request.setResponseCode(500, message=str(err))
        return "FAILURE".encode('utf-8')
    
    request.setResponseCode(200)
    return "SUCCESS".encode('utf-8')

class MyResource(Resource):
    def render_GET(self, request):
        log.info("getting data from previous node...")
        cmd = "/home/root/docker/input-retriever.py"
        return call_python3(cmd, request)


resource = MyResource()
