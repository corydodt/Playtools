"""
Test for the parsing of saves
"""

from twisted.trial import unittest
from playtools.parser import saveparser


class SaveParserTest(unittest.TestCase):
    def test_regular(self):
        """
        Plain jane saves can parse
        """
        t1 = "Fort +9, Ref +6, Will +6"
        t2 = "Fort +9, Ref +6, Will -6"

        parsed = saveparser.parseSaves(t1)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'fort':9, 'ref':6, 'will':6}
        self.assertEqual(actual, expected)

        parsed = saveparser.parseSaves(t2)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'fort':9, 'ref':6, 'will':-6}
        self.assertEqual(actual, expected)

    def test_null(self):
        """
        Saves with nulls parse ok
        """
        t = "Fort +9, Ref -, Will +6"
        parsed = saveparser.parseSaves(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'fort':9, 'ref':0, 'will':6}
        self.assertEqual(actual, expected)
        self.assertEqual(parsed['ref'].other, '-')

    def test_whitespace(self):
        """
        Saves with odd whitespace parse ok
        """
        t = "Fort +9, Ref - , Will +6"
        parsed = saveparser.parseSaves(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'fort':9, 'ref':0, 'will':6}
        self.assertEqual(actual, expected)

    def test_qualifier(self):
        """
        Saves with qualifier messages parse ok
        """
        t = "Fort +14 (+18 against poison), Ref +12, Will +12"
        parsed = saveparser.parseSaves(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'fort':14, 'ref':12, 'will':12}
        self.assertEqual(actual, expected)
        self.assertEqual(parsed['fort'].qualifier, '(+18 against poison)')

    def test_splat(self):
        """
        Saves with splats parse ok
        """
        t = "Fort +9*, Ref +1*, Will -8*"
        parsed = saveparser.parseSaves(t)[0]
        actual = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'fort':9, 'ref':1, 'will':-8}
        self.assertEqual(actual, expected)

        for k in 'fort', 'ref', 'will':
            self.assertEqual(parsed[k].splat, "*")

    def test_crap(self):
        """
        One monster has saves specified as a message..
        """
        t = "As master's saves"
        parsed = saveparser.parseSaves(t)[0]
        bonuses = dict([(k, v.bonus) for k,v in parsed.items()])
        expected = {'fort':0, 'ref':0, 'will':0}
        self.assertEqual(bonuses, expected)
        for k in 'fort', 'ref', 'will':
            self.assertEqual(parsed[k].other, "As master's saves")
