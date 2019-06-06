from twisted.web.resource import Resource

class MyResource(Resource):
    def render_GET(self, request):
        return "calling GET retrieve".encode('utf-8')
    def render_POST(self, request):
        return 'calling POST retrieve'.encode('utf-8')

resource = MyResource()