from twisted.web.resource import Resource
from paraview.web import protocols
from subprocess import call

PYTHON3_BIN = "/pyenv/versions/3.6.7/bin/python"

class MyResource(Resource):
    def render_GET(self, _):
        print("pulling state from S3...")
        exit_code = call("{} /home/root/docker/state_manager.py pull".format(PYTHON3_BIN), shell=True)
        print("exit_code", exit_code)
        return "calling GET state".encode('utf-8')
    def render_POST(self, _):
        print("saving state...")
        save_data = protocols.ParaViewWebSaveData(baseSavePath="/data/save-data")
        save_data.saveData("state.pvsm")
        print("pushing state to S3...")
        exit_code = call("{} /home/root/docker/state_manager.py push".format(PYTHON3_BIN), shell=True)
        print("exit_code", exit_code)
        return 'called POST state'.encode('utf-8')

resource = MyResource()