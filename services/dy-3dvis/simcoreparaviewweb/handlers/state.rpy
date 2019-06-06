from twisted.web.resource import Resource
from paraview.web import protocols
from subprocess import call
import os

class MyResource(Resource):
    def render_GET(self, request):
        return "calling GET state".encode('utf-8')
    def render_POST(self, request):
        print("saving state...")
        save_data = protocols.ParaViewWebSaveData(baseSavePath="/data/save-data")
        save_data.saveData("state.pvsm")
        print("pushing state to S3...")
        exit_code = call("export REQUEST_METHOD=POST;\ /pyenv/versions/3.6.7/bin/python /home/root/cgi_scripts/state_handler.py")
        print("exit_code", exit_code)
        return 'called POST state'.encode('utf-8')

resource = MyResource()