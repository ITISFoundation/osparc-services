from twisted.web.resource import Resource

class MyResource(Resource):
    def render_GET(self, request):
        return "calling GET state".encode('utf-8')
    def render_POST(self, request):
        return 'calling POST state'.encode('utf-8')

resource = MyResource()