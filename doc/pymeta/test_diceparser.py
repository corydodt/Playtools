import unittest

from playtools import diceparser

class DiceParserTestCase(unittest.TestCase):
    def test_reverseFormatDice(self):
        def t(s, ):
            parsed = diceparser.parseDice(s)
            expected = ''.join(s.split()).lower()
            self.assertEqual(expected, str(parsed))

        t(' d10')
        t(' 2d20')
        t('2d20+1')
        t('2d 20+1')
        t('2 d 20- 1')
        t("2d6-2x2sort")
        t("9d6l3-10x2")
        t("9d6H3+10x2")
        t('2')

    def test_parse(self):
        def t(s, exp):
            dexp = diceparser.parseDice(s)
            self.assertEqual(dexp.repList(), exp)

        t('2',            'sn=2 c=1 ds=1 fd= fc= dm=0 r=1 sort=')
        t(' d10',         'sn= c=1 ds=10 fd= fc= dm=0 r=1 sort=')
        t(' 2d10',        'sn= c=2 ds=10 fd= fc= dm=0 r=1 sort=')
        t('2d20x2',       'sn= c=2 ds=20 fd= fc= dm=0 r=2 sort=')
        t('9d6l3',        'sn= c=9 ds=6 fd=l fc=3 dm=0 r=1 sort=')
        t('2d20+1',       'sn= c=2 ds=20 fd= fc= dm=1 r=1 sort=')
        t('2d 20+1',      'sn= c=2 ds=20 fd= fc= dm=1 r=1 sort=')
        t('2 d 20 - 1',   'sn= c=2 ds=20 fd= fc= dm=-1 r=1 sort=')
        t('2d6-2x2sort',  'sn= c=2 ds=6 fd= fc= dm=-2 r=2 sort=sort')
        t('9d6l3-10x2',   'sn= c=9 ds=6 fd=l fc=3 dm=-10 r=2 sort=')
        t('9d6H3+10x2',   'sn= c=9 ds=6 fd=h fc=3 dm=10 r=2 sort=')

        self.assertRaises(RuntimeError, diceparser.parseDice, '2d')

    def test_exportProductions(self):
        """
        Importing the diceparser module enables some parsing productions.
        Verify that these are exported correctly.
        """
        grammar = """<ws> := [ \t]*
            xyz := diceExpression, ws, diceExpression
            abc := dieModifier, ws, dieModifier
            xyzRoot := xyz/abc
            """
        p = parser.Parser(grammar, root='xyzRoot')
        p.parse('1d20 1d20')
        p.parse('+1 -1')

