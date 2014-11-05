import unittest
from bricks.static_manager import OptimizingStaticManager
from bricks.staticfiles import StaticfileOptimizationLevel as Lvl
from bricks.staticfiles import StaticCss, StaticJs
from bricks import Bricks
from bricks.static_manager import static_group_key

def gen_all_static(prefix='a'):
    static_components = []
    i = 0
    for _type, suffix in ((StaticJs, 'js'), (StaticCss, 'css')):
        for level in Lvl:
            for bottom in (False, True):
                i += 1
                name = prefix + str(i)
                cmpnt = _type(
                    name,
                    asset='bricks:test/static/'+name+'.'+suffix,
                    optim=level,
                    bottom=bottom
                )
                static_components.append(cmpnt)
    return static_components

class TestOptimizingStaticManagerGrouping(unittest.TestCase):
    def setUp(self):
        self.bricks = Bricks()
        self.static_manager = self.bricks.add(OptimizingStaticManager)
        self.aComponents = gen_all_static()
        self.bComponents = gen_all_static('b')
        class B:
            depends_on = self.bComponents

            def __init__(self, *_): pass

        class A:
            depends_on = self.aComponents + [B]

            def __init__(self, *_): pass
        self.a = self.bricks.add(A)
        self.b = self.bricks.add(B)
        self.groupdict = self.static_manager.group_all()

    def test_INLINE_NOOPT_grouping(self):
        #veryify all INLINE and NOOPT components are in their own group
        for c in self.aComponents + self.bComponents:
            c = self.bricks.add(c)
            if c.optim in (Lvl.NOOPT, Lvl.INLINE):
                g = self.groupdict[static_group_key(c, None)]
                self.assertEqual(len(g), 1)
                self.assertTrue(c in g)

    def test_CONCAT_grouping(self):
        #verify CONCAT components
        concats = set()
        for c in self.aComponents + self.bComponents:
            c = self.bricks.add(c)
            if c.optim == Lvl.CONCAT:
                concats.add(c)
        for c in concats:
            g = self.groupdict[static_group_key(c, None)]
            self.assertEqual(len(g), 2)
            self.assertTrue(c in g)
            for i in g:
                self.assertEqual(i.bottom, c.bottom)
                self.assertEqual(i.relpath, c.relpath)

    def test_CONCAT_PAGE_grouping(self):
        #verify CONCAT_PAGE components
        for c in self.bComponents:
            c = self.bricks.add(c)
            if c.optim == Lvl.CONCAT_PAGE:
                g = self.groupdict[static_group_key(c, self.b)]
                self.assertTrue(c in g)
                self.assertEqual(len(g), 1)
                g = self.groupdict[static_group_key(c, self.a)]
                self.assertEqual(len(g), 2)
                self.assertTrue(c in g)
                self.assertTrue([i for i in g if i != c][0] not in self.bComponents)

    def test_group_string(self):
        groupstring = self.static_manager.group_string(self.groupdict)
        self.assertEqual(len(groupstring.split('\n\n')), 28)#not a comprehensive test

class TestOptimizingStaticManagerRendering(unittest.TestCase):
    def setUp(self):
        self.bricks = Bricks()
        self.static_manager = self.bricks.add(OptimizingStaticManager)
        self.aComponents = gen_all_static()
        self.bComponents = gen_all_static('b')
        class B:
            depends_on = self.bComponents

            def __init__(self, *_): pass

        class A:
            depends_on = self.aComponents + [B]

            def __init__(self, *_): pass
        self.a = self.bricks.add(A)
        self.b = self.bricks.add(B)

    def test_url_loading(self):
        self.assertFalse(hasattr(self.static_manager, 'group_url_map'))
        groups = self.static_manager.ordered_group(self.static_manager.group_all())
        urls = ['http://localhost:8080/%s' % i for i in range(len(groups))]
        self.static_manager.load_group_urls(urls)
        self.assertEqual(len(self.static_manager.group_url_map), len(groups))
        for component in self.aComponents + self.bComponents:
            component = self.static_manager.components[component]
            urla = self.static_manager.get_group_url(component, self.a)
            urlb = self.static_manager.get_group_url(component, self.b)
            if static_group_key(component, self.a) == static_group_key(component, self.b):
                self.assertEqual(urla, urlb)
            else:
                self.assertNotEqual(urla, urlb)
            self.assertTrue(urla.startswith('http://'))
            self.assertTrue(urlb.startswith('http://'))

if __name__ == '__main__':
    unittest.main()
