import sys

from twisted.trial import unittest
from twisted.python.filepath import FilePath

from playtools import convert as C
from playtools.plugins.skills import skillConverter, SkillConverter
from playtools.test import pttestutil

class MockPlaytoolsIO(object):
    def __init__(self):
        self.n3buf = []
        self.xmlbuf = []

    def writeXml(self, x):
        [self.xmlbuf.append(line) for line in x.split('\n')]

    def writeN3(self, x):
        [self.n3buf.append(line) for line in x.split('\n')]


def skillSource(count):
    for n in range(count):
        yield MockSkill()


class MockSkill(object):
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


class MockConverter(object):
    """This docstring exists only for testing.
    This line should be ignored.
    """


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
        sys.path = [FilePath(__file__).parent()]
        self.assert_(skillConverter in C.getConverters())
        self.assert_(skillConverter is C.getConverter('SkillConverter'))

    def test_skillConverter(self):
        sv = SkillConverter(skillSource(1))
        io = MockPlaytoolsIO()
        sv.n3Preamble(io)
        for skill in sv:
            sv.writePlaytoolsItem(io, skill)
    
        expected = '''@prefix p: <http://thesoftworld.com/2007/property.n3#> .
@prefix c: <http://thesoftworld.com/2007/characteristic.n3#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<> rdfs:title "All d20 SRD Skills" .

:sneakiness
    rdfs:label "Sneakiness";
    p:keyAbility c:str;
    a c:RetryableSkill;
    p:reference <http://www.d20srd.org/srd/skills/sneakiness.htm>;
.
'''.split('\n')

        comparisonGrid = pttestutil.padZip(expected, io.n3buf)
        _msg = pttestutil.formatFailMsg(io.n3buf)
        for eLine, aLine in comparisonGrid:
            self.assertEqual(aLine, eLine, msg=_msg % (eLine, aLine))

        expectedXml = ('<Description xmlns='
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#" about='
            '"http://thesoftworld.com/2007/skill.n3#">'
            '<em xmlns="http://www.w3.org/1999/xhtml">Stuff</em>'
            '</Description>'
        )

        actualXml = '\n'.join(io.xmlbuf)
        _msg = "%s != %s" % (expectedXml, actualXml)
        self.failUnless(
                pttestutil.compareXml(expectedXml, actualXml),
                msg=_msg)

    def test_rdfXmlWrap(self):
        s1 = "hellO"
        ex1 = ('<Description xmlns='
               '"http://www.w3.org/1999/02/22-rdf-syntax-ns#" about='
               '"foo">hellO</Description>'
        )
        a1 = C.rdfXmlWrap(s1, about="foo")
        _msg = "%s != %s" % (a1, ex1)
        self.failUnless(pttestutil.compareXml(a1, ex1), msg=_msg)

        s2 = "abc<p style='stuff'>thingz</p>xyz"
        ex2 = ('<Description xmlns='
               '"http://www.w3.org/1999/02/22-rdf-syntax-ns#" about='
               '"foo">abc<p style='
               '"stuff">thingz</p>xyz</Description>'
        )
        a2 = C.rdfXmlWrap(s2, about="foo")
        _msg = "%s != %s" % (a2, ex2)
        self.failUnless(pttestutil.compareXml(a2, ex2), msg=_msg)

    def test_rdfName(self):
        s1 = "thing"
        s2 = "The Thing. that (we want)"
        self.assertEqual(C.rdfName(s1), "thing")
        self.assertEqual(C.rdfName(s2), "theThingThatWeWant")

    def test_converterDoc(self):
        actual = C.converterDoc(MockConverter())
        self.assertEqual(actual, 
                "This docstring exists only for testing.")

