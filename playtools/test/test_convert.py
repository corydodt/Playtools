import sys

from zope.interface import implements

from rdflib.Namespace import Namespace as NS

from twisted.trial import unittest
from twisted.plugin import IPlugin

from playtools import convert, sparqly
from playtools.plugins.skills import skillConverter
from playtools.test import pttestutil
from playtools.common import this, RDFSNS

from StringIO import StringIO

def skillSource(count):
    """
    Simulate the real skillSource argument to SkillConverter
    """
    for n in range(count):
        yield MockSkill()


class MockSkill(object):
    """
    Simulate a real skill with class attributes
    """
    id = 1
    name = u'Sneakiness'
    subtype = None
    key_ability = u'Str'
    psionic = u'No'
    trained = u'No'
    armor_check = u'-'
    description = u'<em>Stuff</em>'
    skill_check = u'<em>More stuff</em>'
    action = u'Thingie'
    try_again = u'Yes'
    special = u'Hi'
    restriction = 'Stuff is restricted'
    synergy = 'If you have 5 ranks in Doing Stuff you gain a +2 bonus on Sneakiness checks.'
    epic_use = '<p>If you are epic, you rock</p>'
    untrained = None
    full_text = '.........................................<em>stuff</em>'
    reference = 'SRD 3.5 CombinedSkills'


SAMPLE = NS('http://sample.com/2007/mock.n3#')


class MockConverter(object):
    """This docstring exists only for testing.
    This line should be ignored.
    """
    implements(convert.IConverter, IPlugin)
    commandLine = None

    def __init__(self, mockSource):
        self.mockSource = mockSource
        self.db = sparqly.TriplesDatabase(SAMPLE)
        self.db.open(None)

    def label(self):
        return u"mock"

    def next(self):
        return self.mockSource.next()

    def makePlaytoolsItem(self, item):
        self.db.addTriple(SAMPLE.x, SAMPLE.y, SAMPLE.z)

    def writeAll(self, playtoolsIO):
        playtoolsIO.write(self.db.dump())

    def __iter__(self):
        return self

    def preamble(self):
        self.db.addTriple(this, RDFSNS.label, "Mockery")


class Mock2(object):
    # do NOT add a docstring here. This is for testing.
    pass

assert Mock2.__doc__ is None # yeah, I mean it. :-)


class ConvertTestCase(unittest.TestCase):
    def setUp(self):
        """
        Save the elements of C{sys.path}.
        """
        self.originalPath = sys.path[:]

    def tearDown(self):
        """
        Restore C{sys.path} to its original value.
        """
        sys.path[:] = self.originalPath

    def test_getConverters(self):
        """
        Check that our plugins can be found.
        """
        self.assert_(skillConverter in convert.getConverters())
        self.assert_(skillConverter is convert.getConverter('skills'))
        self.assertRaises(KeyError, lambda: convert.getConverter("  ** does not exist  ** "))

    def test_conversion(self):
        """
        Test running a mock converter, ensuring that IConverter is stable
        """
        source = skillSource(1)
        c = MockConverter(source)

        # test preamble
        c.preamble()
        triples = list(c.db.graph)
        self.failUnless((this, RDFSNS.label, 'Mockery') in triples)

        # test label
        self.assertEqual(c.label(), 'mock')

        # test next, __iter__
        for item in c:
            pass
        self.failUnless(isinstance(item, MockSkill))

        # test makePlaytoolsItem
        c.makePlaytoolsItem(item)
        triples = list(c.db.graph)
        self.failUnless((SAMPLE.x, SAMPLE.y, SAMPLE.z) in triples)

        # test writeAll
        io = StringIO()
        c.db.graph.bind('rdfs', RDFSNS)
        c.writeAll(io)

        st = io.getvalue()
        self.failUnless('<> rdfs:label "Mockery".' in st)

    def test_rdfXmlWrap(self):
        """
        Test standard way to produce an RDF/XML statement from some XML markup
        """
        s1 = "hellO"
        ex1 = ('<Description xmlns='
               '"http://www.w3.org/1999/02/22-rdf-syntax-ns#" about='
               '"foo" parseType="Literal"><hi xmlns="bar#">hellO</hi></Description>'
        )
        a1 = convert.rdfXmlWrap(s1, about="foo", predicate=("hi", "bar#"))
        _msg = "%s != %s" % (a1, ex1)
        self.failUnless(pttestutil.compareXml(a1, ex1), msg=_msg)

        s2 = "abc<p style='stuff'>thingz</p>xyz"
        ex2 = ('<Description xmlns='
               '"http://www.w3.org/1999/02/22-rdf-syntax-ns#" about='
               '"foo" parseType="Literal"><bar:hi xmlns:bar="bar">abc<p style='
               '"stuff">thingz</p>xyz</bar:hi></Description>'
        )
        a2 = convert.rdfXmlWrap(s2, about="foo", predicate=("hi", "bar#"))
        _msg = "%s != %s" % (a2, ex2)
        self.failUnless(pttestutil.compareXml(a2, ex2), msg=_msg)

    def test_converterDoc(self):
        """
        Assert that there is a standard way to get the doc from a Converter
        """
        source = skillSource(1)
        actual = convert.converterDoc(MockConverter(source))
        self.assertEqual(actual, "This docstring exists only for testing.")

        actual = convert.converterDoc(Mock2())
        self.assertEqual(actual, "")
