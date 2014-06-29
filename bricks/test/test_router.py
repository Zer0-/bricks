import unittest
from bricks.routing import RouteApi, Route
from webob import Request
from ceramic_forms import Use, And

class TestRequestRoute(unittest.TestCase):
    def setUp(self):
        self.root = Route()
        self.r1 = Route(handler=object())
        self.r2 = Route(handler=object(), handles_subtree=True)
        self.r3 = Route(handler=object())
        self.r4 = Route(handler=object(), handles_subtree=True)
        self.r5 = Route(handler=object())
        self.routemap = self.root + {
            'first': self.r1 + {
                Use(int): self.r2 + {
                    'second': self.r3 + {
                        Use(int): self.r4
                    }
                }
            },
            'not_used': self.r5
        }

    def testRouteMatching(self):
        request = Request.blank('/first/1/one/two/second/2/three/four')
        routeapi = RouteApi(request, self.routemap)
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
        routeapi = RouteApi(request, self.routemap)
        self.assertEqual(routeapi.path, ['first', 1, 'one', 'two', 'second', 2, 'three', 'four'])

    def testVars(self):
        request = Request.blank('/first/1/one/two/second/2/three/four')
        routeapi = RouteApi(request, self.routemap)
        self.assertEqual(routeapi.vars, (1, 2))

    def testTrivialRoot(self):
        request = Request.blank('/')
        routeapi = RouteApi(request, self.routemap)
        self.assertEqual(routeapi.route, self.root)

    def testRouteFinding(self):
        path_route_pairs = [
            ('/first', self.r1),
            ('/first/1000', self.r2),
            ('/first/3/', self.r2),
            ('/first/3/a/b/c/d/e', self.r2),
            ('/first/3/a/b/second', self.r3),
            ('/first/3/a/b/second/3', self.r4),
            ('/first/3/a/b/second/44/c/d/e', self.r4),
        ]
        for path, route in path_route_pairs:
            request = Request.blank(path)
            routeapi = RouteApi(request, self.routemap)
            self.assertEqual(routeapi.route, route)

    def testRoutefindingFailing(self):
        invalid_routes = [
            '/invalid',
            '/first/asdf',
            '/first/asdf/second'
            '/first/3/second/asdf'
        ]
        for path in invalid_routes:
            request = Request.blank(path)
            routeapi = RouteApi(request, self.routemap)
            self.assertEqual(routeapi._matched_routes, 404)

    def testRelative(self):
        request = Request.blank('/first/1/one/two/second/2/three/four')
        routeapi = RouteApi(request, self.routemap)
        self.assertEqual(routeapi.relative, (('one', 'two'), ('three', 'four')))

    def testRoutelist(self):
        from bricks.routing import routeset
        routes = [
            self.root,
            self.r1,
            self.r2,
            self.r3,
            self.r4,
            self.r5
        ]
        routes = set(routes)
        found_routes = routeset(self.routemap)
        self.assertEqual(found_routes, routes)

    def testApiRoutes(self):
        request = Request.blank('/first/1/one/two/second/2/three/four')
        routes = [self.root, self.r1, self.r2, self.r3, self.r4]
        routeapi = RouteApi(request, self.routemap)
        self.assertEqual(routeapi.routes, routes)

class TestPathFinding(unittest.TestCase):
    def setUp(self):
        p_one = Route()
        r = Route(handler=object())
        self.routemap = r + {
            'one': r,
            'const_one': p_one,
            'two': r + {
                'a' : r + {
                    Use(int): r,
                    'six': r
                },
                str: r + {
                    And(Use(int), lambda x: x%2 == 0): r + {
                        'wot': r,
                        'const_two': p_one
                    },
                    lambda x: len(x) == 4: p_one,
                    And(Use(int), lambda x: x%2 != 0): p_one
                }
            }
        }
        self.p_one = p_one

    def testRouteLookup(self):
        request = Request.blank('')
        api = RouteApi(request, self.routemap)
        for path_args, path in [
            ((), ['const_one']),
            (('two', 'four'), ['two', 'two', 'four']),
            (('two', '216'), ['two', 'two', 216, 'const_two']),
            (('two', 216), ['two', 'two', 216, 'const_two']),
            (('two', 11), ['two', 'two', 11]),
        ]:
            found = api.find(self.p_one, path_args)
            self.assertEqual(path, found)

    def testRouteLookupFailure(self):
        request = Request.blank('')
        api = RouteApi(request, self.routemap)
        for path_args in [
            ('wot',),
            ('three', 'six'),
        ]:
            path = api.find(self.p_one, path_args)
            self.assertEqual(path, None)

if __name__ == '__main__':
    unittest.main()
