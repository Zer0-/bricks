import unittest
from pyramid_bricks.render import mako_response, string_response, json_response

class MockResponse:
    pass

class TestRendering(unittest.TestCase):
    def setUp(self):
        self.mock_response = MockResponse()

    def testMakoResponse(self):

        @mako_response("pyramid_bricks:test/test_data/templates/template.mako")
        def mako(_, request, response):
            return {}

        mako(None, None, self.mock_response)
        self.assertEqual(self.mock_response.text, 'Hello World\n\n')

    def testStringResponse(self):
        @string_response
        def stringresp(_, request, response):
            return "hello world"

        stringresp(None, None, self.mock_response)
        self.assertEqual(self.mock_response.text, 'hello world')

    def testJsonResponse(self):
        @json_response
        def js(_, request, response):
            return {'a': [1, 2, 3]}

        from json import loads
        js(None, None, self.mock_response)
        self.assertEqual(loads(self.mock_response.text), {'a': [1, 2, 3]})
