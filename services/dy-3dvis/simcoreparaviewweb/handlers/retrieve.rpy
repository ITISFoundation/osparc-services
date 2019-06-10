from twisted.web.resource import Resource
from subprocess import call

PYTHON3_BIN = "/pyenv/versions/3.6.7/bin/python"

class MyResource(Resource):
    def render_GET(self, _):
        print("getting data from previous node...")
        exit_code = call("{} /home/root/docker/input-retriever.py".format(PYTHON3_BIN), shell=True)
        print("exit_code", exit_code)
        return "calling GET retrieve".encode('utf-8')
    

resource = MyResource()