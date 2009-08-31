"""
Test for the parsing of fulltext abilities.  These are the fulltext
descriptions of a monster's special abilities.
"""
import sys
import traceback
from xml.dom import minidom

from twisted.trial import unittest

from playtools.parser import ftabilityparser
from playtools import fact
from playtools.util import RESOURCE

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class FakeElement(object):
    """
    Fudge doesn't allow you to .provide an __eq__ because of the unusual
    circumstances involved in calling __eq__ (apparently it's called via the
    class rather than the instance).
    """
    def __eq__(self, other):
        return True

class FullTextAbilityParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
    def test_flatten(self):
        fakeEl = FakeElement()

        s = u"""<html foo='bar'/>"""
        doc = minidom.parseString(s)
        actual = ftabilityparser.flatten(doc)
        expected = [(u'html', {u'foo':u'bar'}, fakeEl, [])]
        self.assertEqual(actual, expected)

        s = u"""<html><head /> stuff </html>"""
        doc = minidom.parseString(s)
        actual = ftabilityparser.flatten(doc)
        expected = [(u'html', {}, fakeEl, 
            [(u'head', {}, fakeEl, []),
             (u'#text', {}, u' stuff ', [])])
            ]
        self.assertEqual(actual, expected)

        s = u"""<html><head><title>hello</title><meta /></head><body><div
        la="1">text <p topic="xyz"><b>title</b> other</p>
        stuff</div><div la="2">other</div></body></html>"""
        doc = minidom.parseString(s)
        actual = ftabilityparser.flatten(doc)
        expected = [
                (u'html', {}, fakeEl, [
                    (u'head', {}, fakeEl, [
                        (u'title', {}, fakeEl, [
                            ("#text", {}, u'hello', [])]),
                        (u'meta', {}, fakeEl, [])]),
                    (u'body', {}, fakeEl, [
                        (u'div', {u'la':u'1'}, fakeEl, [
                            ('#text', {}, u'text ', []),
                            (u'p', {u'topic':u'xyz'}, fakeEl, [
                                (u'b', {}, fakeEl, [
                                    ('#text', {}, u'title', [])]),
                                ('#text', {}, u' other', [])]),
                            ('#text', {}, u'\n        stuff', [])]),
                        (u'div', {u'la':u'2'}, fakeEl, [
                            ('#text', {}, u'other', []) 
                            ])])
                        ])
                    ]
        self.assertEqual(actual, expected)

    def test_unescape(self):
        """
        Check utility fn to remove slashes removes them.
        """
        t1 = r"\n<div topic=\"Atropal\" level=\"3\"><p><h3>Atropal</h3></p><table width=\"100%\" border=\"1\" cellpadding=\"2\" cellspacing=\"2\" frame=\"VOID\" rules=\"ROWS\">"
        self.assertEqual(ftabilityparser.unescape(t1),
              "\n<div topic=\"Atropal\" level=\"3\"><p><h3>Atropal</h3></p><table width=\"100%\" border=\"1\" cellpadding=\"2\" cellspacing=\"2\" frame=\"VOID\" rules=\"ROWS\">"
              )

    def test_prepFT(self):
        """
        Check utility function to prep by wrapping in html does it right.
        """
        t1 = r"<div foo=\"bar\" />"
        self.assertEqual(ftabilityparser.prepFT(t1), "<html><div foo=\"bar\" /></html>")

    def test_regular(self):
        """
        Plain jane fulls can parse
        """
        aranea = open(RESOURCE('plugins/monster/monstertext/aranea.htm')).read()
        specAbs = ftabilityparser.parseFTAbilities(aranea, prep=0)
        poison = specAbs[0]
        self.assertEqual(poison.name, "Poison")
        self.assertEqual(poison.useCategory, "Ex")
        self.assertEqual(poison.text, 
                u'<div level="8" topic="Poison">\n<p> Injury, Fortitude DC 13, initial damage 1d6 Str, secondary damage 2d6 Str. The save DC is Constitution-based.</p>\n</div>'
                )

    def formatSpellLike(self, sla):
        return "{0.name}:{0.frequency}:{0.basis}:{0.dc}:{0.casterLevel}:{0.qualifier}".format(sla)

    def test_spellLike(self):
        """
        Monsters with spell-like abilities can parse
        """
        def getSpellLikes(filename):
            """
            Get a list of spell-like abilities by parsing the filename
            """
            monster = open(filename).read()
            specAbs = ftabilityparser.parseFTAbilities(monster, prep=0)
            ret = []
            for ab in specAbs:
                if ab.useCategory == 'Sp':
                    ret.append(self.formatSpellLike(ab))
            return ret

        asserted = getSpellLikes(RESOURCE('plugins/monster/monstertext/pixie.htm'))
        stringy = '\n'.join(map(self.formatSpellLike, asserted))
        self.assertEqual(stringy, """\
lesser confusion:1/day:Charisma:14:8:
dancing lights:1/day:Charisma::8:
detect chaos:1/day:Charisma::8:
detect good:1/day:Charisma::8:
detect evil:1/day:Charisma::8:
detect law:1/day:Charisma::8:
detect thoughts:1/day:Charisma:15:8:
dispel magic:1/day:Charisma::8:
entangle:1/day:Charisma:14:8:
permanent image:1/day:Charisma:19:8:visual and auditory elements only
polymorph:1/day:Charisma::8:self only
:::::<p>One pixie in ten can use <i>irresistible dance</i> (caster level 8th) once per day.</p>""")

        asserted = getSpellLikes(RESOURCE('plugins/monster/monstertext/dreamLarva.htm')).read()
        stringy = '\n'.join(map(self.formatSpellLike, asserted))
        self.assertEqual(stringy, """\
fly:At will:Charisma:23 + spell level:31:
haste:At will:Charisma:23 + spell level:31:
nightmare:At will:Charisma:23 + spell level:31:
prismatic spray:At will:Charisma:23 + spell level:31:
dreamscape:2/day:Charisma:23 + spell level:31:""")


    def test_null(self):
        """
        Null fulls parse ok
        """
        t = ""
        parsed = ftabilityparser.parseFTAbilities(t)
        expected = []
        self.assertEqual(parsed, expected)


class HUGEFullTextAbilityParserTest(unittest.TestCase):
    """
    Test every known Special stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            stat1 = monster.full_text

            try:
                if stat1:
                    act = [monster.name, ftabilityparser.parseFTAbilities(stat1) and None]
            except:
                f = traceback.format_exc(sys.exc_info()[2])
                self.assertTrue(False,
                        "{x}\n{0}\n{1}\n".format(monster.name, stat1, x=f))

