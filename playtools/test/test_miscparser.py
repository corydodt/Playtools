"""
Test for the parsing of saves
"""

from twisted.trial import unittest

from playtools.parser import misc
from playtools import fact
from playtools.common import C

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class MiscParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
    def test_initiative(self):
        """
        Initiatives drop the parenthetical part
        """
        t1 = "+7 (Dex)"
        t2 = "+7"
        t3 = "+6 (+2 Dex, +4 Improved Initiative)"
        t4 = "+18 (+14 Dex, +4 Improved Initiativ"

        self.assertEqual(misc.parseInitiative(t1), 7)
        self.assertEqual(misc.parseInitiative(t2), 7)
        self.assertEqual(misc.parseInitiative(t3), 6)
        self.assertEqual(misc.parseInitiative(t4), 18)

    def test_challengeRating(self):
        """
        Challenge ratings with notes parse
        """
        t1 = u"7"
        t2 = u"7 (x, y+ z)"
        t3 = u"7 (x); 8 (y)"
        t4 = u"7; 8"
        self.assertEqual(misc.parseChallengeRating(t1), [(7, None)])
        self.assertEqual(misc.parseChallengeRating(t2), [(7, '(x, y+ z)')])
        self.assertEqual(misc.parseChallengeRating(t3), [(7, '(x)'), (8, '(y)')])
        self.assertEqual(misc.parseChallengeRating(t4), [(7, None), (8, None)])

    def test_size(self):
        """
        Abilities with nulls parse ok
        """
        t1 = "Medium"
        t2 = "tiny"
        t3 = "colossal+"
        t4 = "dIminutive"
        self.assertEqual(misc.parseSize(t1), C.medium)
        self.assertEqual(misc.parseSize(t2), C.tiny)
        self.assertEqual(misc.parseSize(t3), C.colossalPlus)
        self.assertEqual(misc.parseSize(t4), C.diminutive)

