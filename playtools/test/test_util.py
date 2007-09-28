
from twisted.trial import unittest

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

