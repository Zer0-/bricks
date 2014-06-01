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

if __name__ == '__main__':
    unittest.main()
