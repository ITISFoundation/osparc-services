import logging
import os

from twisted.web.resource import Resource
from paraview.web import protocols
from subprocess import Popen, PIPE

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
    def render_GET(self, request):        
        log.info("pulling state from S3...")
        cmd = "/home/root/docker/state_manager.py pull"
        return call_python3(cmd, request)

    def render_POST(self, request):
        log.info("saving state...")
        save_data = protocols.ParaViewWebSaveData(baseSavePath=os.environ.get("PARAVIEW_INPUT_PATH"))
        save_data.saveData(os.environ.get("SIMCORE_STATE_FILE"))
        cmd = "/home/root/docker/state_manager.py push"
        return call_python3(cmd, request)

resource = MyResource()