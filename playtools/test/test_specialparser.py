"""
Test for the parsing of specials
"""
import sys
import traceback

from twisted.trial import unittest

from playtools.parser import specialparser
from playtools import fact

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class SpecialParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
    def compare(self, stat, expected):
        """
        Compare the result of parsing stat to the expected string
        """
        _a = specialparser.parseSpecialQualities(stat)
        actual = self.fmt(_a)
        self.assertEqual(actual, expected)

    def fmt(self, qs):
        """
        Format a quality for comparison
        """
        ret = []
        for quality in qs:
            kw = '/'.join(["%s:%s" % (k,v) for (k,v) in quality.kw.items()])
            ret.append("kw={kw} type={q.type} name={q.name}".format(
                kw=kw, q=quality))
        return '\n'.join(ret)

    def test_empty(self):
        self.assertEqual(specialparser.parseSpecialQualities("-"), [])

    def test_regular(self):
        """
        Plain jane Specials can parse
        """
        self.compare("alternate form", "kw= type=noArgumentQuality name=alternate form")
        self.compare("Rend 4d6+18", "kw=damage:4d6+18 type=damaging name=Rend")
        self.compare("Rend 4d6+18, sonic blast", "kw=damage:4d6+18 type=damaging name=Rend\nkw= type=unknown name=sonic blast")
    test_regular.todo = "many more expressions to check still"


class HUGESpecialParserTest(unittest.TestCase):
    """
    Test every known Special stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            stat1 = monster.special_attacks
            stat2 = monster.special_qualities

            try:
                if stat1:
                    act = [monster.name, specialparser.parseSpecialQualities(stat1) and None]
            except:
                f = traceback.format_exc(sys.exc_info()[2])
                self.assertTrue(False,
                        "{x}\n{0}\n{1}\n".format(monster.name, stat1, x=f))

            try:
                if stat2:
                    act = [monster.name, specialparser.parseSpecialQualities(stat2) and None]
            except:
                f = traceback.format_exc(sys.exc_info()[2])
                self.assertTrue(False,
                        "{x}\n{0}\n{1}\n".format(monster.name, stat2, x=f))
        specialparser.printFrequenciesOfUnknowns()

