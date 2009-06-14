import unittest

from playtools.parser import diceparser
from simpleparse import parser

class DiceParserTestCase(unittest.TestCase):
    def test_reverseFormatDice(self):
        def t(s, ):
            parsed = diceparser.parseDice(s)
            expected = ''.join(s.split()).lower()
            f = parsed.format()
            self.assertEqual(expected, f)
            self.assertTrue(type(f) is unicode)

        t(' d10')
        t(' 2d20')
        t('2d20+1')
        t('2d 20+1')
        t('2 d 20- 1')
        t("2d6-2x2sort")
        t("9d6l3-10x2")
        t("9d6H3+10x2")
        t('2')
        t(u'2')
        t(u"2d6-2x2sort")

    def test_parse(self):

        tests = [ # {{{
            (True, ' d10'),
            (True, ' 2d20'),
            (True, '2d20+1'),
            (True, '2d 20+1'),
            (True, '2 d 20- 1'),
            (True, "2d6-2x2sort"),
            (True, "9d6l3-10x2"),
            (True, "9d6H3+10x2"),
            (True, '2'),
            (False, '2d'),
        ] # }}}

        dp = diceparser.diceParser

        for expect, test in tests:
            proc = diceparser.Processor()
            suc, children, next = dp.parse(test, processor=proc)
            self.assertEqual(suc, expect)
            if expect:
                self.assertEqual(next, len(test), '%s!=%s "%s"' % (next,
                    len(test), test))

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

