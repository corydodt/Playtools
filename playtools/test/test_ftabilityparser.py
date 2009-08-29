"""
Test for the parsing of fulltext abilities.  These are the fulltext
descriptions of a monster's special abilities.
"""
import sys
import traceback

from twisted.trial import unittest

from playtools.parser import ftabilityparser
from playtools import fact
from playtools.util import RESOURCE

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class FullTextAbilityParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
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

    def test_spellLike(self):
        """
        Monsters with spell-like abilities can parse
        """
        pixie = open(RESOURCE('plugins/monster/monstertext/pixie.htm')).read()
        specAbs = ftabilityparser.parseFTAbilities(pixie, prep=0)
        for ab in specAbs:
            if ab.useCategory == 'Sp':
                self.assertEqual(ab.text, u"""<div level="8" topic="Spell-Like Abilities">
<p> 1/day-<i>lesser confusion</i> (DC 14), <i>dancing lights</i>,  <i>detect chaos</i>,  <i>detect good</i>,  <i>detect evil</i>,  <i>detect law</i>,  <i>detect thoughts</i> (DC 15), <i>dispel magic</i>,  <i>entangle</i> (DC 14), <i>permanent image</i> (DC 19; visual and auditory elements only), <i>polymorph</i> (self only). Caster level 8th. The save DCs are Charisma-based.</p>
<p>One pixie in ten can use <i>irresistible dance</i> (caster level 8th) once per day.</p>
</div>""")
                break
        else:
            assert 0, "Did not find spell-like ability"

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

