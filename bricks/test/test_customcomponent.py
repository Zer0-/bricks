import unittest
from bricks.custom import customizable

class A(metaclass=customizable):
    custom_attributes = ('wot',)

class B(metaclass=customizable):
    custom_attributes = ('bee',)

    def silly(self):
        return 'haha' + self.bee

class TestCustomClass(unittest.TestCase):
    def testBadInstantiation(self):
        self.assertRaises(TypeError, A)
        self.assertRaises(TypeError, A, 'Batman')
        A('myA', wot='asdf')#noraises

    def testCreatesType(self):
        myA = A('myA', wot='asdf')
        self.assertTrue(type(myA) is type)

    def testName(self):
        myA = A('Batman', wot='asdf')
        self.assertEqual(myA.__name__, 'Batman')

    def testHasCustomAttr(self):
        myA = A('myA', wot='asdf')
        self.assertEqual(myA.wot, 'asdf')

    def testClsCreatesInst(self):
        myA = A('myA', wot='asdf')
        ainst = myA()
        self.assertTrue(isinstance(ainst, myA))
        self.assertTrue(type(ainst) is myA)

    def testKeepsAttribs(self):
        myB = B('Bee', bee='s')
        self.assertEqual(myB().silly(), 'hahas')

    def testSubclass(self):
        class C(A):
            m = 'm'

        myc = C('myC', wot='fdsa')
        self.assertEqual(myc.wot, 'fdsa')
        self.assertEqual(myc.m, 'm')

    def testSubclassSubclass(self):
        class C(A):
            m = 'm'

        class D(C):
            m = 'monkey'

        d = D('myD', wot='fdsa')
        self.assertEqual(d.m, 'monkey')
        self.assertEqual(d().m, 'monkey')

    def testCustomSubclass(self):
        myB = B('Bee', bee='s')

        class C(myB):
            def silly(self):
                return 'span' + self.bee

        self.assertEqual(C().silly(), 'spans')

    def testMySubclass(self):
        class V(metaclass=customizable):
            custom_attributes = ('m',)
            thing = 'television'

        class M(V):
            thing = 'popcorn'

        class N(M):
            pass

        self.assertEqual(V('myV', m='asdf').thing, 'television')
        self.assertEqual(N('myN', m='asdf').thing, 'popcorn')
        self.assertEqual(N('myN', m='asdf')().thing, 'popcorn')

if __name__ == '__main__':
    unittest.main()
