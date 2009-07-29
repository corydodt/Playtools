"""
Test for the parsing of skills
"""

from twisted.trial import unittest

from playtools.parser import skillparser
from playtools import fact

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class SkillParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
    def test_regular(self):
        """
        Plain jane Skills can parse
        """
        t1 = "Spot +1"
        t2 = "Concentration -6, Hide +7, Move Silently +5, Psicraft +7, Ride +5, Spot +3"

        parsed1 = skillparser.parseSkills(t1)[0]
        actual = dict([(i.skillName, i.value) for i in parsed1])
        expected = {"Spot": 1}
        self.assertEqual(actual, expected)

        parsed2 = skillparser.parseSkills(t2)[0]
        actual = dict([(i.skillName, i.value) for i in parsed2])
        expected = {'Concentration':-6, 
                'Hide':7,
                'Move Silently':5, 
                'Psicraft':7, 
                'Ride':5, 
                'Spot':3}
        self.assertEqual(actual, expected)

    def test_null(self):
        """
        Null skills parse ok
        """
        t = "-"
        parsed = skillparser.parseSkills(t)[0]
        expected = []
        self.assertEqual(parsed, expected)

    def test_whitespace(self):
        """
        Saves with odd whitespace parse ok
        """
        t = "Str 9, Dex 10, Con - , Int 12, Wis 13, Cha 14"
        parsed = skillparser.parseSkills(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':9, 'dex':10, 'con':0, 'int':12, 'wis':13, 'cha':14}
        self.assertEqual(actual, expected)

    def test_splat(self):
        """
        Saves with splats parse ok
        """
        t = "Str 9*, Dex 10*, Con 11*, Int 12*, Wis 13*, Cha 14*"
        parsed = skillparser.parseSkills(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':9, 'dex':10, 'con':11, 'int':12, 'wis':13, 'cha':14}
        self.assertEqual(actual, expected)

        for k in 'str dex con int wis cha'.split():
            self.assertEqual(parsed[k].splat, "*", k)

    def test_qualifier(self):
        """
        Skills with qualifier messages parse ok
        """
        t = "Str 35, Dex 6, Con -, Int 1 (or as controlling spirit), Wis 11 (or as controlling spirit), Cha 10 (or as controlling spirit)"
        parsed = skillparser.parseSkills(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'str':35, 'dex':6, 'con':0, 'int':1, 'wis':11, 'cha':10}
        self.assertEqual(actual, expected)

        for stat in ['int', 'wis', 'cha']:
            self.assertEqual(parsed[stat].qualifier, '(or as controlling spirit)', stat)


class HUGESkillParserTest(unittest.TestCase):
    """
    Test every known Skill stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            # we aren't actually making any assertions about Skills except
            # that they can be processed.  The "exp" construction is here so
            # that the assertEqual at the end will have a string to tell us
            # *which* monster failed, if one does.
            exp = [monster.name, None]

            stat = monster.Skills

            # get('name') as a proxy for checking that the monster actually
            # loaded ok.
            act = [monster.name, skillparser.parseSkills(stat) and None]
            self.assertEqual(exp, act)

tests = ( # {{{
"""-
Speak Language (elven, common)
Speak Language (any five), Jump +16*
Concentration +19, Craft or Knowledge (any three) +19, Diplomacy +22, Escape Artist +19, Hide +19, Intimidate +20, Listen +23, Move Silently +19, Sense Motive +19, Spot +23, Use Rope +4 (+6 with bindings)
Knowledge (psionics) +12, Speak Language (ninjish), Jump +1
Hide +15, Move Silently +7, Listen +6, Spot +2
Hide +1000, Listen +5, Spot +5
Hide +9, Intimidate +12, Knowledge (psionics) +12, Listen +14, Psicraft +12, Search +12, Sense Motive +12, Spot +14* (comma, comma, ninjas)
Concentration +17, Hide +7, Jump +16, Knowledge (arcana) +12, Knowledge (psionics) +12, Knowledge (the planes) +12, Listen +22, Move Silently +11, Psicraft +12, Search +12, Sense Motive +14, Spot +22
Concentration +14, Diplomacy +17, Jump +0, Knowledge (any two) +15, Listen +16, Search +15, Sense Motive +16, Spellcraft +15 (+17 scrolls), Spot +16, Survival +4 (+6 following tracks), Tumble +15, Use Magic Device +15 (+17 scrolls)
Bluff + 15, Concentration +11 (+15 when manifesting defensively), Hide +14, Listen +14, Move Silently +16
Jump +16 (or as controlling spirit)
Climb +38, Knowledge (psionics, arcane) +31, Listen +30, Psicraft +31, Spot +30
Climb +38 (+39 on a good day)*
Listen +11, Move Silently +7, Spot +11
Climb +14*, Listen +6, Move Silently +6, Search +2, Spot +6
Hide +22, Listen +7, Sense Motive +7, Spot +7
Climb +12, Jump +20, Listen +7, Spot +8
Listen +10
Bluff +10*, Diplomacy +6, Disguise +10*, Intimidate +6, Listen +6, Sense Motive +6, Spot +6
Climb and Skip +2, Jump +2
""".splitlines()) # }}}

if __name__ == '__main__':
    for t in tests:
        print t
        parsed = parseSkills(t)
        print parsed
