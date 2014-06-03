import unittest
from webob import Request
from pyramid_bricks.bricks import create_app

class MockMain:
    def __call__(self, request):
        from webob import Response
        response = Response()
        response.text = "hello world"
        return response

class TestAppCreation(unittest.TestCase):
    def testAppCreation(self):
        app = create_app(MockMain)
        request = Request.blank('/some/url/doesnt/matter')
        response = request.get_response(app)
        self.assertEqual(response.body, b"hello world")

    def testMainComponentCreation(self):
        from pyramid_bricks.routing import Route
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

if __name__ == '__main__':
    unittest.main()
