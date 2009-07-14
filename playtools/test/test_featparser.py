"""
Test for the parsing of feats
"""

from twisted.trial import unittest

from playtools.parser import featparser
from playtools import fact
from playtools.common import C
from playtools.test.pttestutil import pluck

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class FeatParserTest(unittest.TestCase):
    """
    Test nuances of parsing feats
    """
    def test_simple(self,):
        """
        Basic list of feats
        """
        ll = "Combat Expertise, Mobility"
        self.assertEqual(pluck(featparser.parseFeats(ll)[0], 'name'), 
                ['Combat Expertise', 'Mobility'])

    def test_qualified(self):  
        ll = "Combat Expertise (la, la), Mobility"
        parsed = featparser.parseFeats(ll)[0]
        self.assertEqual(pluck(parsed, 'name'), ['Combat Expertise', 'Mobility'])
        self.assertEqual(pluck(parsed, 'qualifier'), ['la, la', None])

    def test_timesTaken(self):
        ll = "Combat Expertise (la, la), Mobility (x2)"
        parsed = featparser.parseFeats(ll)[0]
        self.assertEqual(pluck(parsed, 'name'), ['Combat Expertise', 'Mobility'])
        self.assertEqual(pluck(parsed, 'timesTaken'), [None, 2])



class HUGEFeatParserTest(unittest.TestCase):
    """
    Test every known feat stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            # we aren't actually making any assertions about feats except
            # that they can be processed.  The "exp" construction is here so
            # that the assertEqual at the end will have a string to tell us
            # *which* monster failed, if one does.
            exp = [monster.name, None]

            for stat in [monster.feats, 
                    monster.bonus_feats,
                    monster.epic_feats]:
                # get('name') as a proxy for checking that the monster actually
                # loaded ok.
                try:
                    act = [monster.name, featparser.parseFeats(stat) and None]
                    self.assertEqual(exp, act)
                finally:
                    """print monster.name"""


tests = ( # {{{
"""-
Ability Focus (poison), Alertness, Flyby Attack
Iron Will, Toughness (2)
Alertness, Empower Spell, Flyby Attack, Hover, Improved Initiative, Maximize Spell, Power Attack, Weapon Focus (bite), Weapon Focus (claw), Wingover
Alertness, Improved Critical (chain), Improved Initiative
Multiattack, Toughness
Cleave, Improved Sunder, Iron Will, Multiattack, Power Attack, Weapon Focus (spiked chain)
Alertness, Iron Will, Track
Blind-Fight, Cleave, Combat Reflexes, Improved Initiative, Power Attack
Great Fortitude, Ride-by Attack, Spirited Charge
Alertness, Combat Reflexes, Improved Initiative, Skill Focus (Sense Motive), Skill Focus (Survival), Stealthy, Track
Alertness, Toughness
Weapon Focus (rapier)
Alertness
Alertness, Diehard, Endurance, Toughness (2)
Flyby Attack, Improved Initiative, Improved Critical (bite), Iron Will, Multiattack, Weapon Focus (eye ray), Weapon Focus (bite)
Alertness, Empower Spell, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Alertness, Hover, Improved Initiative, Weapon Focus (bite)
Alertness, Weapon Focus (morningstar)
Alertness, Empower Spell, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Alertness, Awesome Blow, Blind-Fight, Cleave, Combat Reflexes, Dodge, Great Cleave, Improved Bull Rush, Improved Initiative, Iron Will, Power Attack, Toughness (6)
Weapon Focus (longbow), item creation feat (any one)
Alertness, Blind-Fight, Cleave, Empower Spell, Flyby Attack, Hover, Improved Initiative, Maximize Spell, Power Attack, Snatch, Weapon Focus (bite), Weapon Focus (claw), Wingover
Alertness, Empower Spell, Flyby Attack, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Lycanthrope Hybrid Feats (same as human form)
Blinding Speed (x2), Epic Prowess (x2), Epic Toughness (x4), Epic Will, Superior Initiative
""".splitlines()) # }}}

if __name__ == '__main__':
    for flist in tests:
        print flist
        parsed = parseFeats(flist)
        print parsed
