import os
import re
from xml.dom import minidom

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
        s4 = "1st-level astral construct"
        self.assertEqual(util.rdfName(s1), "thing")
        self.assertEqual(util.rdfName(s2), "theThingThatWeWant")
        self.assertEqual(util.rdfName(s3), "theThingThatWeWant")
        self.assertEqual(util.rdfName(s4), "_1stLevelAstralConstruct")

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

    def test_doNodes(self):
        """
        We can arbitrarily manipulate nodes by criteria
        """
        t1 = minidom.parseString("<div>x<div>y<EX>z </EX></div>abc</div>")
        def findText(n):
            return (n.nodeName == '#text')

        def makeItRock(n):
            n.data = "ROCK"

        list(util.doNodes(t1, findText, makeItRock))
        expected = u"<div>ROCK<div>ROCK<EX>ROCK</EX></div>ROCK</div>"

        self.assertEqual(t1.firstChild.toxml(), expected)

    def test_findNodes(self):
        """
        We can search for nodes by particular criteria
        """
        t1 = minidom.parseString("<div>x<div>y<EX>z </EX></div>abc</div>")
        expected = t1.getElementsByTagName('EX')[0]
        def findZ(n):
            return (n.childNodes and
                    hasattr(n.childNodes[0], "data") and 
                    n.childNodes[0].data == "z ")
        self.assertEqual(list(util.findNodes(t1, findZ)), [expected])

        t2 = minidom.parseString("<div>x<EX name='hi'>y<div>z </div></EX>abc</div>")
        expected = t2.getElementsByTagName('EX')[0]
        def findHi(n):
            return hasattr(n, 'getAttribute') and n.getAttribute('name') == 'hi'
        self.assertEqual(list(util.findNodes(t2, findHi)), [expected])

    def test_gatherText(self):
        """
        We can collect the text from a dom tree
        """
        t1 = minidom.parseString("<div>x<div>y<div>z </div></div>abc</div>")
        self.assertEqual(util.gatherText(t1), u"x y z  abc")
        t2 = minidom.parseString("<x>ab c</x>")
        self.assertEqual(util.gatherText(t2), u"ab c")

    def test_flushLeft(self):
        """
        Triple-quoted strings are annoying to work with - this function makes
        sure they get properly aligned.
        """
        input = """        this
        function
        sucks
        """
        self.assertEqual(util.flushLeft(input), "this\nfunction\nsucks\n")
