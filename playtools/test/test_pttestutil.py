"""
Unit tests for the test utility suite
"""
from twisted.trial import unittest

from rdflib import BNode

from playtools.test.pttestutil import padZip, compareXml, IsomorphicTestableGraph, pluck
from playtools.common import P, C


class TestUtilTestCase(unittest.TestCase):
    """
    Test the utilities used in testing themselves.
    """
    def test_padZip(self):
        """
        padZip should return a sequence, padded with whatevers for missing items
        akin to SQL's "FULL JOIN"
        """
        l1 = [1,2,3]
        l2 = []
        l3 = [1,2,3,4]
        self.assertEqual(padZip(l1, l2), [(1, None), (2, None), (3, None)])
        self.assertEqual(padZip(l1, l2, 1), [(1, 1), (2, 1), (3, 1)])
        self.assertEqual(padZip(l1, l3), [(1, 1), (2, 2), (3, 3), (None, 4)])

    def test_compareXml(self):
        """
        compareXml should look for differences between two xml trees
        """
        # differences in attributes should cause a failed comparison
        s1 = """<a>hello</a>"""
        s2 = """<a y="1" x="1">hello</a>"""
        s3 = """<a x="1" y="1">hello</a>"""
        self.assert_(compareXml(s1, s1))
        self.failIf(compareXml(s1, s2))
        # ... but attribute order should not cause failed comparison
        self.assert_(compareXml(s3, s2))

        # test differences in deep elements, and text after deep elements
        s4 = """<a>hello<b>1</b>2</a>"""
        s5 = """<a>hello<b>1</b>3</a>"""
        s6 = """<a>hello<b>2</b>2</a>"""
        self.failIf(compareXml(s4, s5))
        self.failIf(compareXml(s4, s6))
        self.failIf(compareXml(s6, s5))
        
        # elements present in LHS and missing from RHS are compared as None,
        # make sure this case is handled (comparisons with None are always
        # False)
        s7 = """<a><b /></a>"""
        s8 = """<a><b /><b /></a>"""
        self.failIf(compareXml(s7, s8))
        self.failIf(compareXml(s8, s7))

    def test_isomorphicGraphs(self):
        """
        IsomorphicTestableGraph has comparison operations - make sure they fit our use case
        """
        g1 = IsomorphicTestableGraph()
        g2 = IsomorphicTestableGraph()

        self.assertEqual(g1, g2)

        g1.bind('c', C)
        g1.add((C.x, C.y, C.z))
        # don't add a binding to g2
        g2.add((C.x, C.y, C.z))
        self.failIfEqual(g1, g2)

        # now add the binding and make sure they are again the same
        g2.bind('c', C)
        self.assertEqual(g1, g2)

        # both graphs should compare the same if they contain nodes with
        # (the same) unbound namespaces
        g1.add((P.x, P.y, P.z))
        g2.add((P.x, P.y, P.z))

        self.assertEqual(g1, g2)

        # check BNodes
        g1.add((BNode(), P.y, P.z))
        g2.add((BNode(), P.y, P.z))

        self.assertEqual(g1, g2)

        # check formulae

    def test_pluck(self):
        """
        The pluck utility pulls attributes out of a list of things
        """
        class C: pass
        c1 = C(); c1.x = 1
        c2 = C(); c2.x = 2
        c3 = C(); c3.x = 3
        c4 = C(); c4.x = 4
        ll = [c1,c2,c3,c4]
        self.assertEqual(pluck(ll, 'x'), [1,2,3,4])
        c1.c = C(); c1.c.x = 7
        c2.c = C(); c2.c.x = 8
        c3.c = C(); c3.c.x = 9
        c4.c = C(); c4.c.x = 10
        self.assertEqual(pluck(ll, 'c', 'x'), [7,8,9,10])
