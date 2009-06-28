"""
Test for the parsing of treasure
"""

from twisted.trial import unittest
from playtools.parser import treasureparser
from playtools.common import C
from playtools import fact

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']


DEFAULT = object()

class TreasureParserTest(unittest.TestCase):
    def test_aggregate(self):
        """
        Treasures with an aggregate value will parse
        """
        self.check("Standard",
                {C.Coins:C.standardTreasure,C.Goods:C.standardTreasure,C.Items:C.standardTreasure})
        self.check("double standard",
                {C.Coins:C.doubleStandardTreasure,C.Goods:C.doubleStandardTreasure,C.Items:C.doubleStandardTreasure})
        self.check("Triple standard",
                {C.Coins:C.tripleStandardTreasure,C.Goods:C.tripleStandardTreasure,C.Items:C.tripleStandardTreasure})
        self.check("none",
                {C.Coins:C.noTreasure,C.Goods:C.noTreasure,C.Items:C.noTreasure},
                {C.Coins:None, C.Goods:None, C.Items:None}, None)
        self.check("half Standard",
                {C.Coins:C.halfStandardTreasure,C.Goods:C.halfStandardTreasure,C.Items:C.halfStandardTreasure})

    def test_aggregateQualifier(self):
        """
        Aggregate treasures with qualifier messages parse ok
        """
        self.check("standard (including +1 hide, +1 greatclub and ring of pro +1)",
                {C.Coins:C.standardTreasure,
                    C.Goods:C.standardTreasure,
                    C.Items:C.standardTreasure},
                other="(including +1 hide, +1 greatclub and ring of pro +1)")
        self.check("standard (including equipment)", other="(including equipment)")

    def test_parts(self):
        """
        Treasures split into 3 parts parse ok

        """
        def check(t, expected):
            parsed, other = treasureparser.parseTreasures(t)[0]
            actual = dict([(k, v.value) for k,v in parsed.items()])
            self.assertEqual(actual, expected)
            self.assertEqual(other, None)

        check('1/10 coins; 50% goods; standard items', 
                {C.Coins:'1/10', 
                    C.Goods:C.halfStandardTreasure, 
                    C.Items:C.standardTreasure})
        check('1/5 coins; 50% goods; 50% items', 
                {C.Coins:'1/5', 
                    C.Goods:C.halfStandardTreasure,
                    C.Items:C.halfStandardTreasure})
        check('no coins; standard goods; double items', 
                {C.Coins:C.noTreasure,
                    C.Goods:C.standardTreasure,
                    C.Items:C.doubleStandardTreasure})
        check('50% coins; 50% goods; 50% items', 
                {C.Coins:C.halfStandardTreasure, 
                    C.Goods:C.halfStandardTreasure, 
                    C.Items:C.halfStandardTreasure})
        check('no coins; 50% goods; 50% items', 
                {C.Coins:C.noTreasure, 
                    C.Goods:C.halfStandardTreasure,
                    C.Items:C.halfStandardTreasure})
        check('50% coins; double goods; standard items', 
                {C.Coins:C.halfStandardTreasure, 
                    C.Goods:C.doubleStandardTreasure, 
                    C.Items:C.standardTreasure})
        check('no coins; double goods; standard items', 
                {C.Coins:C.noTreasure, 
                    C.Goods:C.doubleStandardTreasure, 
                    C.Items:C.standardTreasure})
        check('standard coins; double goods; standard items', 
                {C.Coins:C.standardTreasure, 
                    C.Goods:C.doubleStandardTreasure, 
                    C.Items:C.standardTreasure})
        check('1/10 coins; 50% goods; 50% items', 
                {C.Coins:'1/10', 
                    C.Goods:C.halfStandardTreasure, 
                    C.Items:C.halfStandardTreasure})

    def test_partsQualifier(self):
        """
        Treasures with qualifier messages parse ok
        """
        self.check("standard coins; standard goods (gems only); standard items",
                {C.Coins:C.standardTreasure, 
                    C.Goods:C.standardTreasure, 
                    C.Items:C.standardTreasure},
                {C.Coins:None,
                    C.Goods:'(gems only)',
                    C.Items:None})
        self.check("standard coins; standard goods (nonflammables only); standard items (nonflammables only)",
                {C.Coins:C.standardTreasure, 
                    C.Goods:C.standardTreasure, 
                    C.Items:C.standardTreasure},
                {C.Coins:None,
                    C.Goods:'(nonflammables only)',
                    C.Items:'(nonflammables only)'})
        self.check("no coins; 1/4 goods (stone only); no items",
                {C.Coins:C.noTreasure, 
                    C.Goods:'1/4',
                    C.Items:C.noTreasure},
                {C.Coins:None,
                    C.Goods:'(stone only)',
                    C.Items:None})
        self.check("no coins; 50% goods (metal or stone only); 50% items (no scrolls)",
                {C.Coins:C.noTreasure, 
                    C.Goods:C.halfStandardTreasure,
                    C.Items:C.halfStandardTreasure},
                {C.Coins:None,
                    C.Goods:'(metal or stone only)',
                    C.Items:'(no scrolls)'})
        #

    def check(self, t, values=DEFAULT, qualifiers=DEFAULT, other=DEFAULT):
        """
        Common implementation of all the tests
        """
        parsed, actualOther = treasureparser.parseTreasures(t)[0]
        actual1 = dict([(k, v.value) for k,v in parsed.items()])
        actual2 = dict([(k, v.qualifier) for k,v in parsed.items()])
        if values is not DEFAULT:
            self.assertEqual(actual1, values)
        if qualifiers is not DEFAULT:
            self.assertEqual(actual2, qualifiers)
        if other is not DEFAULT:
            self.assertEqual(actualOther, other)

    def test_none(self):
        """
        Monsters with no treasure
        """
        self.check(None, {C.Coins:C.noTreasure, 
                        C.Goods:C.noTreasure, 
                        C.Items:C.noTreasure}, other=None)

        def check(t, expected1, expected2, expected3):
            parsed, other = treasureparser.parseTreasures(t)[0]
            actual1 = dict([(k, v.value) for k,v in parsed.items()])
            actual2 = dict([(k, v.qualifier) for k,v in parsed.items()])
            self.assertEqual(actual1, expected1)
            self.assertEqual(actual2, expected2)

            self.assertEqual(other, expected3)

    def test_specificItems(self):
        """
        Treasures with specific items specified, in parts or aggregate, can
        parse

        """
        def check(t, expected1, expected2, expected3):
            parsed, other = treasureparser.parseTreasures(t)[0]
            actual1 = dict([(k, v.value) for k,v in parsed.items()])
            actual2 = dict([(k, v.qualifier) for k,v in parsed.items()])
            self.assertEqual(actual1, expected1)
            self.assertEqual(actual2, expected2)

            self.assertEqual(other, expected3)

        self.check("double standard; plus +4 half-plate armor and gargantuan +3 adamantine warhammer",
                    {C.Coins:C.doubleStandardTreasure, 
                        C.Goods:C.doubleStandardTreasure, 
                        C.Items:C.doubleStandardTreasure},
                    {C.Coins:None,
                        C.Goods:None,
                        C.Items:None},
                    'plus +4 half-plate armor and gargantuan +3 adamantine warhammer')
        self.check("standard coins; double goods; standard items; plus 1d4 magic weapons",
                    {C.Coins:C.standardTreasure, 
                        C.Goods:C.doubleStandardTreasure, 
                        C.Items:C.standardTreasure},
                    {C.Coins:None,
                        C.Goods:None,
                        C.Items:None},
                "plus 1d4 magic weapons")
        self.check("standard coins; double goods; no items; plus +1 vorpal greatsword and +1 flaming whip",
                    {C.Coins:C.standardTreasure, 
                        C.Goods:C.doubleStandardTreasure, 
                        C.Items:C.noTreasure},
                    {C.Coins:None,
                        C.Goods:None,
                        C.Items:None},
                "plus +1 vorpal greatsword and +1 flaming whip")
        self.check("standard; plus rope and +1 flaming composite longbow (+5 str bonus)",
                    {C.Coins:C.standardTreasure, 
                        C.Goods:C.standardTreasure, 
                        C.Items:C.standardTreasure},
                    {C.Coins:None,
                        C.Goods:None,
                        C.Items:None},
                "plus rope and +1 flaming composite longbow (+5 str bonus)")
        self.check("double coins; double goods (nonflammables only); double items (nonflammables only); plus +3 longspear",
                    {C.Coins:C.doubleStandardTreasure, 
                        C.Goods:C.doubleStandardTreasure, 
                        C.Items:C.doubleStandardTreasure},
                    {C.Coins:None,
                        C.Goods:'(nonflammables only)',
                        C.Items:'(nonflammables only)'},
                "plus +3 longspear")

class HUGETreasureParserTest(unittest.TestCase):
    """
    Test every known treasure stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            # we aren't actually making any assertions about treasures except
            # that they can be processed.  The "exp" construction is here so
            # that the assertEqual at the end will have a string to tell us
            # *which* monster failed, if one does.
            exp = [monster.name, None]

            stat = monster.treasure

            # get('name') as a proxy for checking that the monster actually
            # loaded ok.
            act = [monster.name, treasureparser.parseTreasures(stat) and None]
            self.assertEqual(exp, act)
