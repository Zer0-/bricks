import unittest
from webob import Request
from pyramid_bricks.bricks import create_app
from pyramid_bricks.routing import Route

def _hworld():
    from webob import Response
    response = Response()
    response.text = "hello world"
    return response

class MockMain:
    def __call__(self, request):
        return _hworld()

class MockComponent:
    def GET(self, request):
        return _hworld()

class TestAppCreation(unittest.TestCase):
    def testAppCreation(self):
        app = create_app(MockMain)
        request = Request.blank('/some/url/doesnt/matter')
        response = request.get_response(app)
        self.assertEqual(response.body, b"hello world")

    def testMainComponentCreation(self):
        from pyramid_bricks.bricks import BaseMC, mc_from_routemap

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

        def mock_init(inst, *routes):
            self.assertEqual(set(routes), set(routelist))

        BaseMC.__init__ = mock_init
        main_component = mc_from_routemap(routemap)
        self.assertEqual(set(main_component.depends_on), set(routelist))
        create_app(main_component)

    def testAll(self):
        from pyramid_bricks.bricks import app_from_routemap
        routemap = Route(handler=MockComponent)
        app = app_from_routemap(routemap)
        req = Request.blank('/')
        res = req.get_response(app)
        self.assertEqual(res.body, b'hello world')

if __name__ == '__main__':
    unittest.main()
