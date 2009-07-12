"""
Test for the parsing of saves
"""

from twisted.trial import unittest

from playtools.parser import misc
from playtools import fact
from playtools.common import C, FAM

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
        self.assertEqual(misc.parseInitiative("+7 (Dex)"), 7)
        self.assertEqual(misc.parseInitiative("+7"), 7)
        self.assertEqual(misc.parseInitiative("+6 (+2 Dex, +4 Improved Initiative)"), 6)
        self.assertEqual(misc.parseInitiative("+18 (+14 Dex, +4 Improved Initiativ"), 18)

    def test_challengeRating(self):
        """
        Challenge ratings with notes parse
        """
        self.assertEqual(misc.parseChallengeRating(u"7"), [(7, None)])
        self.assertEqual(misc.parseChallengeRating(u"7 (x, y+ z)"), [(7, '(x, y+ z)')])
        self.assertEqual(misc.parseChallengeRating(u"7 (x); 8 (y)"), [(7, '(x)'), (8, '(y)')])
        self.assertEqual(misc.parseChallengeRating(u"7; 8"), [(7, None), (8, None)])

    def test_size(self):
        """
        Abilities with nulls parse ok
        """
        self.assertEqual(misc.parseSize("Medium"), C.medium)
        self.assertEqual(misc.parseSize("tiny"), C.tiny)
        self.assertEqual(misc.parseSize("colossal+"), C.colossalPlus)
        self.assertEqual(misc.parseSize("dIminutive"), C.diminutive)

    def test_family(self):
        """
        Very simple family parser works
        """
        self.assertEqual(misc.parseFamily("Abomination"), FAM.abomination)
        self.assertEqual(misc.parseFamily("Abnegation"), "Abnegation")
