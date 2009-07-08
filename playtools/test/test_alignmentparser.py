"""
Test for the parsing of saves
"""

from twisted.trial import unittest

from playtools.parser import alignmentparser
from playtools import fact
from playtools.common import C

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class AlignmentParserTest(unittest.TestCase):
    """
    Test nuances of parsing alignments
    """
    def test_singleAlways(self):
        """
        Alignments with exactly one true alignment option work
        """
        def t(s, expected):
            self.assertEqual(alignmentparser.parseAlignment(s),
                    expected)
            #

        t(None, [[C.noAlignment]])
        t('Always lawful Good', [[C.lawfulGood]])
        t('Always CHAOTIC evil ', [[C.chaoticEvil]])
        t('Always neutral', [[C.neutralNeutral]])
        t('Always neutral evil', [[C.neutralEvil]])

    def test_qualifiedSingle(self):
        """
        A single alignment token with a qualifier parses correctly
        """
        def t(s, expected):
            self.assertEqual(alignmentparser.parseAlignment(s),
                    expected)
            #

        t('Usually lawful good', [[C.lawfulGood, 'Usually']])
        t('Often neutral', [[C.neutralNeutral, 'Often']])
        t('Often neutral (ugly)', [[C.neutralNeutral, 'Often; ugly']])
    
    def test_simpleAny(self):
        """
        An alignment starting with "any" returns the correct choices
        """
        def t(s, expected):
            self.assertEqual(sorted(alignmentparser.parseAlignment(s)),
                    sorted(expected))
            #

        t('Any chaotic', [
            [C.chaoticGood,],
            [C.chaoticNeutral,],
            [C.chaoticEvil,],
            ])
        t('Any evil', [
            [C.lawfulEvil,],
            [C.neutralEvil,],
            [C.chaoticEvil,],
            ])
        t('Any', [
            [C.lawfulGood,],
            [C.neutralGood,],
            [C.chaoticGood,],
            [C.lawfulNeutral,],
            [C.neutralNeutral,],
            [C.chaoticNeutral,],
            [C.lawfulEvil,],
            [C.neutralEvil,],
            [C.chaoticEvil,],
            ])

    def test_simpleChoice(self):
        """
        An alignment using "or" returns the correct choices
        """
        def t(s, expected):
            self.assertEqual(sorted(alignmentparser.parseAlignment(s)),
                    sorted(expected))
            #

        t('Neutral evil or neutral', [
            [C.neutralEvil,],
            [C.neutralNeutral,],
            ])
        t('Lawful evil or chaotic evil', [
            [C.lawfulEvil,],
            [C.chaoticEvil,],
            ])

    def test_qualifiedMultiple(self):
        """
        A alignment token with multiple possibilities, with a qualifier,
        parses correctly
        """
        def t(s, expected):
            self.assertEqual(sorted(alignmentparser.parseAlignment(s)),
                    sorted(expected))
            #

        t('Usually any evil', [
            [C.lawfulEvil, 'Usually'],
            [C.neutralEvil, 'Usually'],
            [C.chaoticEvil, 'Usually'],
            ])
        t('Any (as master)', [
            [C.lawfulGood, '(as master)'],
            [C.neutralGood, '(as master)'],
            [C.chaoticGood, '(as master)'],
            [C.lawfulNeutral, '(as master)'],
            [C.neutralNeutral, '(as master)'],
            [C.chaoticNeutral, '(as master)'],
            [C.lawfulEvil, '(as master)'],
            [C.neutralEvil, '(as master)'],
            [C.chaoticEvil, '(as master)'],
            ])
        t('Often lawful good or Usually lawful neutral (deep only) or Usually neutral (Deep only)',
                [
                    [C.lawfulGood, 'Often'],
                    [C.lawfulNeutral, 'Usually; deep only'],
                    [C.neutralNeutral, 'Usually; Deep only'],
                    ])
        t('Usually chaotic good or Usually neutral (Wood only)',
                [
                    [C.chaoticGood, 'Usually'],
                    [C.neutralNeutral, 'Wood only; usually']
                    ])
        t('Usually chaotic neutral or neutral evil or chaotic evil',
                [
                    [C.chaoticNeutral, 'Usually'],
                    [C.neutralEvil, 'Usually'],
                    [C.chaoticEvil, 'Usually'],
                    ])
        t('Usually neutral good or neutral evil',
                [
                    [C.neutralGood, 'Usually'],
                    [C.neutralEvil, 'Usually'],
                    ])


class HUGEAlignmentParserTest(unittest.TestCase):
    """
    Test every known alignment stat against the parser
    """
    def xxtest_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            # we aren't actually making any assertions about alignments except
            # that they can be processed.  The "exp" construction is here so
            # that the assertEqual at the end will have a string to tell us
            # *which* monster failed, if one does.
            exp = [monster.name, None]

            stat = monster.alignment

            # get('name') as a proxy for checking that the monster actually
            # loaded ok.
            try:
                act = [monster.name, alignmentparser.parseAlignment(stat) and None]
                self.assertEqual(exp, act)
            finally:
                print monster.name
