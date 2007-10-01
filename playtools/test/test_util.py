import os

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
