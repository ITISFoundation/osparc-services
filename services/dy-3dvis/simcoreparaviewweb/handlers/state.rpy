import logging

from twisted.web.resource import Resource
from paraview.web import protocols
from subprocess import call

log = logging.getLogger(__file__)

PYTHON3_BIN = "/pyenv/versions/3.6.7/bin/python"


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
    def render_GET(self, _):        
        log.info("pulling state from S3...")
        cmd = "/home/root/docker/state_manager.py pull"
        return call_python3(cmd)

    def render_POST(self, _):
        log.info("saving state...")
        cmd = "/home/root/docker/state_manager.py push"
        return call_python3(cmd)

resource = MyResource()