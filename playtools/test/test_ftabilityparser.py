"""
Test for the parsing of fulltext abilities.  These are the fulltext
descriptions of a monster's special abilities.
"""

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
    def test_regular(self):
        """
        Plain jane fulls can parse
        """
        aranea = open(RESOURCE('playtools/plugins/monster/aranea.htm')).read()
        parsed = ftabilityparser.parseFTAbilities(aranea)
        poison = parsed[0]
        self.assertEqual(poison.name, "Poison")
        self.assertEqual(poison.useCategory, "Ex")
        self.assertEqual(poison.text, 
                "Injury, Fortitude DC 13, initial damage 1d6 Str, secondary damage 2d6 Str. The save DC is Constitution-based."
                )

    def test_null(self):
        """
        Null fulls parse ok
        """
        t = ""
        parsed = skillparser.parseFTAbilities(t)
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
                    act = [monster.name, specialparser.parseSpecialQualities(stat1) and None]
            except:
                f = traceback.format_exc(sys.exc_info()[2])
                self.assertTrue(False,
                        "{x}\n{0}\n{1}\n".format(monster.name, stat1, x=f))

