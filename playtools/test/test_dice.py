
import unittest

from .. import dice
from ..parser import diceparser

class DiceTestCase(unittest.TestCase):
    def test_roll(self):
        self.assertEqual(dice.roll(diceparser.parseDice('5'), -1).next().sum(), 4)
        self.assertEqual(dice.roll(diceparser.parseDice('5d1'), 1).next().sum(), 6)

    def test_parse(self):
        for d in [
                'd6xz',                   # repeat not a number
                '1d',                     # left out die size
                '1d6l3l3', '1d6h3l3',     # can't specify more than one filter
                '1d6h+1',                 # can't leave the die count out of the filter
                '1d6h2+1',                # can't keep more dice than you started with
                '',                       # empty should be an error
                '1d6+5 1d1',              # multiple expressions
                ]:
            self.assertRaises(RuntimeError, dice.parse, d)

        for n in xrange(30):
            self.assertEqual(dice.parse('5')[0].sum(),              5)
            self.assertEqual(dice.parse('5x3')[2].sum(),            5)
            self.assertEqual(dice.parse('5+1x3')[2].sum(),          6)
            self.assertTrue(1  <= dice.parse('d6')[0].sum()         <= 6)
            self.assertTrue(3  <= dice.parse('3d6')[0].sum()        <= 18)
            self.assertTrue(1  <= dice.parse('1d  6')[0].sum()      <= 6)
            self.assertTrue(3  <= dice.parse('d6+2')[0].sum()       <= 8)
            self.assertTrue(-1 <= dice.parse('d 6 -2')[0].sum()     <= 4)
            self.assertTrue(4  <= dice.parse('2d6+ 2')[0].sum()     <= 14)
            self.assertTrue(0  <= dice.parse('2d6-2')[0].sum()      <= 10)
            self.assertTrue(4  <= dice.parse('9d6h3+1x2')[0].sum()  <= 19)
            self.assertTrue(2  <= dice.parse('9d6L3-1x2')[0].sum()  <= 17)

