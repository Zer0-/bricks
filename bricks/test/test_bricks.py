import unittest
from webob import Request
from bricks.app_bricks import Bricks, wsgi, BaseMC
from bricks.routing import Route
from bricks.httpexceptions import HTTPForbidden

class MockMain:
    def __call__(self, request, response):
        response.text = "hello world"

class MockComponent:
    def GET(self, request, response):
        response.text = "hello world"

    def POST(self, request, response):
        return HTTPForbidden()

class TestAppCreation(unittest.TestCase):
    def testAppCreation(self):
        b = Bricks()
        mc = b.add(MockMain)
        app = wsgi(mc)
        request = Request.blank('/some/url/doesnt/matter')
        response = request.get_response(app)
        self.assertEqual(response.body, b"hello world")

    def testMainComponentCreation(self):

        root = Route()
        r1 = Route()
        r2 = Route()
        r3 = Route()

        routemap = root + {
            'first': r1 + {
                'second': r2,
                'third': r3
            }
        }

        routelist = [root, r1, r2, r3]

        class MC(BaseMC):
            depends_on = [routemap]

        b = Bricks()
        mc = b.add(MC)
        self.assertEqual(set(mc.depends_on), set(routelist))
        wsgi(mc)

    def testAll(self):
        routemap = Route(handler=MockComponent)
        b = Bricks()
        class MC(BaseMC):
            depends_on = [routemap]
        mc = b.add(MC)
        app = wsgi(mc)
        req = Request.blank('/')
        res = req.get_response(app)
        self.assertEqual(res.body, b'hello world')

    def testHttpException(self):
        routemap = Route(handler=MockComponent)
        b = Bricks()
        class MC(BaseMC):
            depends_on = [routemap]
        mc = b.add(MC)
        app = wsgi(mc)
        req = Request.blank('/')
        req.method = 'POST'
        res = req.get_response(app)
        body = str(res.body).lower()
        self.assertTrue('forbidden' in body)

if __name__ == '__main__':
    unittest.main()
