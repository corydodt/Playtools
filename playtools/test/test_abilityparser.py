"""
Test for the parsing of saves
"""

from twisted.trial import unittest

from playtools.parser import abilityparser
from playtools import fact

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class AbilityParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
    def test_regular(self):
        """
        Plain jane abilities can parse
        """
        t1 = "Str 9, Dex 10, Con 11, Int 12, Wis 13, Cha 14"
        t2 = "Str 9, Dex 10, Con -11, Int 12, Wis 13, Cha 14"

        parsed = abilityparser.parseAbilities(t1)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':9, 'dex':10, 'con':11, 'int':12, 'wis':13, 'cha':14}
        self.assertEqual(actual, expected)

        parsed = abilityparser.parseAbilities(t2)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':9, 'dex':10, 'con':-11, 'int':12, 'wis':13, 'cha':14}
        self.assertEqual(actual, expected)

    def test_null(self):
        """
        Abilities with nulls parse ok
        """
        t = "Str 9, Dex 10, Con -, Int 12, Wis 13, Cha 14"
        parsed = abilityparser.parseAbilities(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':9, 'dex':10, 'con':0, 'int':12, 'wis':13, 'cha':14}
        self.assertEqual(actual, expected)
        self.assertEqual(parsed['con'].other, '-')

    def test_whitespace(self):
        """
        Saves with odd whitespace parse ok
        """
        t = "Str 9, Dex 10, Con - , Int 12, Wis 13, Cha 14"
        parsed = abilityparser.parseAbilities(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':9, 'dex':10, 'con':0, 'int':12, 'wis':13, 'cha':14}
        self.assertEqual(actual, expected)

    def test_splat(self):
        """
        Saves with splats parse ok
        """
        t = "Str 9*, Dex 10*, Con 11*, Int 12*, Wis 13*, Cha 14*"
        parsed = abilityparser.parseAbilities(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':9, 'dex':10, 'con':11, 'int':12, 'wis':13, 'cha':14}
        self.assertEqual(actual, expected)

        for k in 'str dex con int wis cha'.split():
            self.assertEqual(parsed[k].splat, "*", k)

    def test_qualifier(self):
        """
        Abilities with qualifier messages parse ok
        """
        t = "Str 35, Dex 6, Con -, Int 1 (or as controlling spirit), Wis 11 (or as controlling spirit), Cha 10 (or as controlling spirit)"
        parsed = abilityparser.parseAbilities(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':35, 'dex':6, 'con':0, 'int':1, 'wis':11, 'cha':10}
        self.assertEqual(actual, expected)

        for stat in ['int', 'wis', 'cha']:
            self.assertEqual(parsed[stat].qualifier, '(or as controlling spirit)', stat)


class HUGEAbilityParserTest(unittest.TestCase):
    """
    Test every known ability stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            # we aren't actually making any assertions about abilities except
            # that they can be processed.  The "exp" construction is here so
            # that the assertEqual at the end will have a string to tell us
            # *which* monster failed, if one does.
            exp = [monster.name, None]

            stat = monster.abilities

            # get('name') as a proxy for checking that the monster actually
            # loaded ok.
            act = [monster.name, abilityparser.parseAbilities(stat) and None]
            self.assertEqual(exp, act)
