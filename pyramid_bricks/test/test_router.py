import unittest
from pyramid_bricks.routing import routing
from webob import Request

class Route(dict):
    def __init__(
        self,
        permissions=(),
        handles_subtree=False
    ):
        self.permissions = permissions
        self.handles_subtree = handles_subtree

    def __add__(self, subtree):
        self.update(subtree)
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
        request = Request.blank('/other_stuff/asdf')
        self.assertEqual(routing(url_tree, request), 404)
        request = Request.blank('/asdf/non_existant')
        self.assertEqual(routing(url_tree, request), 404)
        request = Request.blank('/asdf/target/too_far')
        self.assertEqual(routing(url_tree, request), 404)

    def testSubtreeHandling(self):
        target_route = Route(handles_subtree=True)
        url_tree = Route() + {
            'subtrees': target_route
        }
        request = Request.blank('/subtrees')
        self.assertEqual(routing(url_tree, request), target_route)
        request = Request.blank('/subtrees/one')
        self.assertEqual(routing(url_tree, request), target_route)
        request = Request.blank('/subtrees/one/two/three')
        self.assertEqual(routing(url_tree, request), target_route)

    def testSubtreeNextpart(self):
        target_route = Route()
        url_tree = Route() + {
            'subtrees': Route(handles_subtree=True) + {
                'next_part': target_route
            }
        }
        request = Request.blank('/subtrees/one/and/two/next_part')
        self.assertEqual(routing(url_tree, request), target_route)

    def testSchemaRoute(self):
        from ceramic_forms import Use, And
        first_target = Route()
        target_route = Route()
        second_target = Route()
        url_tree = Route() + {
            'asdf': Route() + {
                str: first_target
            },
            Use(int): Route() + {
                'target': target_route,
                And(Use(int), lambda x: (x % 2) == 0): second_target
            },
            'other_stuff': Route()
        }
        request = Request.blank('/asdf/55a5')
        self.assertEqual(routing(url_tree, request), first_target)
        request = Request.blank('/123/target')
        self.assertEqual(routing(url_tree, request), target_route)
        request = Request.blank('/3215/36')
        self.assertEqual(routing(url_tree, request), second_target)
        request = Request.blank('/3215/35')
        self.assertEqual(routing(url_tree, request), 404)

    def testSchemaSubtreeRoute(self):
        from ceramic_forms import Use, And
        target_route = Route(handles_subtree=True)
        url_tree = Route() + {
            str: target_route
        }
        request = Request.blank('/somestring/')
        self.assertEqual(routing(url_tree, request), target_route)
        request = Request.blank('/somestring/one/two/three')
        self.assertEqual(routing(url_tree, request), target_route)

class TestRequestRouteApi(unittest.TestCase):
    def testVars(self):
        from ceramic_forms import Use
        url_tree = Route() + {
            Use(int): Route() + {
                str: Route()
            }
        }
        request = Request.blank('/1234/something')
        route = routing(url_tree, request)
        vars = request.route.vars
        self.assertEqual(vars, [1234, 'something'])

#New code (refactor above)
from ceramic_forms import Use
from pyramid_bricks.routing import RequestRoute

class TestRequestRoute(unittest.TestCase):
    def setUp(self):
        self.root = Route()
        self.r1 = Route()
        self.r2 = Route(handles_subtree=True)
        self.r3 = Route()
        self.r4 = Route(handles_subtree=True)
        self.routemap = self.root + {
            'first': self.r1 + {
                Use(int): self.r2 + {
                    'second': self.r3 + {
                        Use(int): self.r4
                    }
                }
            }
        }

    def testRouteMatching(self):
        request = Request.blank('/first/1/one/two/second/2/three/four')
        routeapi = RequestRoute(request, self.routemap)
        shouldmatch = [
            ('/', self.root),
            ('first', self.r1),
            (1, self.r2),
            ('one', self.r2),
            ('two', self.r2),
            ('second', self.r3),
            (2, self.r4),
            ('three', self.r4),
            ('four', self.r4)
        ]
        self.assertEqual(routeapi._matched_routes, shouldmatch)

    def testTransformedPath(self):
        request = Request.blank('/first/1/one/two/second/2/three/four')
        routeapi = RequestRoute(request, self.routemap)
        self.assertEqual(routeapi.path, ['first', 1, 'one', 'two', 'second', 2, 'three', 'four'])

    def testVars(self):
        request = Request.blank('/first/1/one/two/second/2/three/four')
        routeapi = RequestRoute(request, self.routemap)
        self.assertEqual(routeapi.vars, [1, 2])

if __name__ == '__main__':
    unittest.main()
