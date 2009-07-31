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
        t2 = "Concentration -6, Hide +7, Move Silently +5, Psicraft +7, Ride +5, Spot +0"

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
                'Spot':0}
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
        t = "Hide + 15,  Move Silently +7 , Listen +6, Spot +2 "
        parsed = skillparser.parseSkills(t)[0]
        actual = dict([(i.skillName, i.value) for i in parsed])
        expected = {'Hide': 15, 'Move Silently': 7, 'Listen': 6, 'Spot': 2}
        self.assertEqual(actual, expected)

    def test_splat(self):
        """
        Saves with splats parse ok
        """
        t1 = "Climb +14*"
        parsed = skillparser.parseSkills(t1)[0]
        actual = dict([(i.skillName, [i.value, i.splat]) for i in parsed])
        expected = {"Climb":[14, "*"]}
        self.assertEqual(actual, expected)

        t2 = "Bluff +10*, Diplomacy +6, Disguise +10*, Intimidate +6, Listen +6"
        parsed = skillparser.parseSkills(t2)[0]
        actual = dict([(i.skillName, [i.value, i.splat]) for i in parsed])
        expected = {"Bluff": [10, "*"], "Diplomacy": [6, None], "Disguise": [10, "*"], 
                "Intimidate": [6, None], "Listen": [6, None]}
        self.assertEqual(actual, expected)

    def test_qualifier(self):
        """
        Skills with qualifier messages parse ok
        """
        t1 = "Jump +16 (or as controlling spirit)"
        parsed = skillparser.parseSkills(t1)[0]
        actual = dict([(i.skillName, [i.value, i.qualifier]) for i in parsed])
        expected = {'Jump': [16, "or as controlling spirit"]}
        self.assertEqual(actual, expected)

        # qualifiers with commas and shit.
        # psionics is a subskill, not a qualifier.
        t2 = "Hide +9, Knowledge (psionics, etc) +12, Spot +14* (comma, comma, ninjas)"
        parsed = skillparser.parseSkills(t2)[0]
        actual = dict([(i.skillName, [i.value, i.qualifier]) for i in parsed])
        expected = {'Hide': [9, None], 
                'Knowledge': [12, None], 
                'Spot': [14, 'comma, comma, ninjas']}
        self.assertEqual(actual, expected)

    def test_speakLanguages(self):
        """
        Speak Languages is handled correctly
        """
        t1 = "Speak Language (elven, common)"
        parsed = skillparser.parseSkills(t1)[0]
        actual = dict([(i.skillName, i.subSkills) for i in parsed])
        expected = {'Speak Language': ['elven', 'common']}
        self.assertEqual(actual, expected)

        t2 = "Speak Language (any five), Jump +16"
        parsed = skillparser.parseSkills(t2)[0]
        actual = dict([(i.skillName, i.subSkills) for i in parsed])
        expected = {'Speak Language': ['any five'], 'Jump': []}
        self.assertEqual(actual, expected)

    def test_subSkills(self):
        """
        Subskills are gathered
        """
        t1 = "Concentration +17, Knowledge (arcana, the planes) +12, Knowledge (psionics) +12, Listen +22"
        parsed = skillparser.parseSkills(t1)[0]
        actual = {}
        for i in parsed:
            actual[(i.skillName, tuple(i.subSkills))] = [i.value, i.qualifier]
        expected = {('Concentration',()): [17, None],
                ('Knowledge',('arcana', 'the planes')): [12, None],
                ('Knowledge',('psionics',)): [12, None],
                ('Listen',()): [22, None],
                }
        self.assertEqual(actual, expected)

        t2 = "Concentration +17, Knowledge (arcana) +12 (+14 while smoking crack)"
        parsed = skillparser.parseSkills(t2)[0]
        actual = {}
        for i in parsed:
            if i.subSkills:
                subs = tuple(i.subSkills)
            else:
                subs = None
            actual[(i.skillName, subs)] = [i.value, i.qualifier]
        expected = {('Concentration',None):[17, None],
                ('Knowledge',('arcana',)):[12, '+14 while smoking crack'],
                }
        self.assertEqual(actual, expected)


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

            stat = monster.skills

            if stat:
                act = [monster.name, skillparser.parseSkills(stat) and None]
                self.assertEqual(exp, act)

