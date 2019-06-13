from twisted.web.resource import Resource
from subprocess import Popen, PIPE

PYTHON3_BIN = "/pyenv/versions/3.6.7/bin/python"

class MyResource(Resource):
    def render_GET(self, request):
        print("getting data from previous node...")
        cmd = "{} /home/root/docker/input-retriever.py".format(PYTHON3_BIN)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        output, err = process.communicate()
        # exit_code = call("{} /home/root/docker/input-retriever.py".format(PYTHON3_BIN), shell=True)
        if process.returncode != 0:
            print("error while retrieval: ", err)
            request.setResponseCode(500)
            return "FAILURE retrieving data".encode('utf-8')
        print(output)
        request.setResponseCode(200)
        return "SUCCESS retrieving data".encode('utf-8')


resource = MyResource()
