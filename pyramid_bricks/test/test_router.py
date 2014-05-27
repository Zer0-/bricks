import unittest
from pyramid_bricks.routing import routing
from webob import Request

class Route:
    pass

class TestRouter(unittest.TestCase):
    def testTrivialRoot(self):
        r = Route()
        url_tree = {
            '/': r
        }
        request = Request.blank('/')
        self.assertEqual(routing(url_tree, request), r)

if __name__ == '__main__':
    unittest.main()
