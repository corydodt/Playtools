import os
import re

from twisted.trial import unittest
from twisted.python.util import sibpath

from playtools import util

class UtilTestCase(unittest.TestCase):

    def test_rdfName(self):
        """
        Test ability to convert weird names into rdf strings in a standard way
        """
        s1 = "thing"
        s2 = "The Thing. that (we want)"
        s3 = "The Thing, that (we want)"
        self.assertEqual(util.rdfName(s1), "thing")
        self.assertEqual(util.rdfName(s2), "theThingThatWeWant")
        self.assertEqual(util.rdfName(s3), "theThingThatWeWant")

    def test_filenameAsUri(self):
        """
        filenameAsUri should accept only strings and return file:// uris
        """
        self.assertRaises(Exception, util.filenameAsUri, 2)
        here = lambda f: os.getcwd() + '/' + f
        self.assertEqual(util.filenameAsUri('x'), 'file://%s' % (here('x'),))
        self.assertEqual(util.filenameAsUri('/x/y/z'), 'file:///x/y/z')

    def test_prefixen(self):
        """
        Prefixes determined for items are stable
        """
        from rdflib.Graph import Graph
        g = Graph()
        corp = sibpath(__file__, 'corp.n3')
        g.load(corp, format='n3')
        prefixes = dict(g.namespaces())
        res = g.query("BASE <http://corp.com/staff#> SELECT ?x ?y ?z { ?x a <http://www.w3.org/2000/01/rdf-schema#Class> } ORDER BY ?x ?y")

        l = list(res)
        rx1 = r':Employee'
        x1 = util.prefixen(prefixes, l[0][0], )
        self.assertTrue(re.match(rx1, x1) is not None, '%s != %s' % (rx1, x1))

        res = g.query("BASE <http://corp.com/staff#> SELECT ?x ?y ?z { ?x ?y ?z } ORDER BY ?x ?y")
        l = list(res)
        rx2 = r'{_:[a-zA-Z0-9]+}'
        x2 = util.prefixen(prefixes, l[-1][0], )
        self.assertTrue(re.match(rx2, x2) is not None, '%s != %s' % (rx2, x2))
