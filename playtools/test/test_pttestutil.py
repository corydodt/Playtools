"""
Unit tests for the test utility suite
"""
from twisted.trial import unittest

from rdflib.Graph import Graph

from playtools.test.pttestutil import padZip, compareXml, compareGraphs
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

    def test_compareGraphs(self):
        """
        compareGraphs should make sure the two graphs are isomorphic and use
        the same prefixes.
        """
        g1 = Graph()
        g2 = Graph()

        self.failUnless(compareGraphs(g1, g2))

        g1.bind('c', C)
        g1.add((C.x, C.y, C.z))
        # don't add a binding to g2
        g2.add((C.x, C.y, C.z))
        self.failIf(compareGraphs(g1, g2))

        # now add the binding and make sure they are again the same
        g2.bind('c', C)
        self.failUnless(compareGraphs(g1, g2))

        # both graphs should compare the same if they contain nodes with
        # (the same) unbound namespaces
        g1.add((P.x, P.y, P.z))
        g2.add((P.x, P.y, P.z))

        self.failUnless(compareGraphs(g1, g2))

