from pyramid_bricks.bricks import app_from_routemap
from pyramid_bricks.routing import Route
from webob import Response

class TestView:
    def GET(self, request, response):
        response.text = 'you are here: root, ' + ', '.join(request.route.path)

routemap = Route(handler=TestView, handles_subtree=True)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    from werkzeug.debug import DebuggedApplication
    app = app_from_routemap(routemap)
    app = DebuggedApplication(app, evalex=True)
    make_server('', 8080, app).serve_forever()
