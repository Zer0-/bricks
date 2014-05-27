import unittest
from pyramid_bricks.routing import routing
from webob import Request

class Route:
    def __init__(self):
        self.dict = {}

    def __getitem__(self, key):
        return self.dict.__getitem__(key)

    def __contains__(self, key):
        return self.dict.__contains__(key)

    def __add__(self, subtree):
        self.dict = subtree
        return self

class TestRouter(unittest.TestCase):
    def testTrivialRoot(self):
        r = Route()
        request = Request.blank('/')
        self.assertEqual(routing(r, request), r)

    def testSimpleRouteTree(self):
        target_route = Route()
        second_target = Route()
        url_tree = Route() + {
            'asdf': Route() + {
                'target': target_route,
                'second_target': second_target
            },
            'other_stuff': Route()
        }
        request = Request.blank('/asdf/target')
        self.assertEqual(routing(url_tree, request), target_route)
        request = Request.blank('/asdf/second_target')
        self.assertEqual(routing(url_tree, request), second_target)

if __name__ == '__main__':
    unittest.main()
