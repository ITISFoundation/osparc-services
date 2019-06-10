from twisted.web.resource import Resource

# import logging
# from pathlib import Path


class MyResource(Resource):
    def render_POST(self, request):
        return 'called POST state'.encode('utf-8')
# form = cgi.FieldStorage()
# server_hostname = form["hostname"].value
# server_port = form["port"].value
# log = logging.getLogger(__name__)
# _INPUT_FILE = Path(r"/home/root/trigger/server_port")

# with _INPUT_FILE.open(mode='w') as fp:
#     fp.write("{hostname}:{port}".format(hostname=server_hostname, port=server_port))
