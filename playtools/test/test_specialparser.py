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

class SimpleSpecialParserTest(unittest.TestCase):
    """
    Test nuances of parsing simple specials
    """
    def fmt(self, parsed):
        return "{0.name}:{0.useCategory}".format(parsed)

    def test_regular(self):
        t = 'Antimagic Field (Ex), Frightful Presence (Ex), Horrific Appearance (su), Magic Immunity (Ex), Negative Energy Affinity (Su), Stench (EX)'
        self.assertEqual(map(self.fmt, specialparser.parseSimpleSpecial(t)),
                ["Antimagic Field:ex",
                 "Frightful Presence:ex",
                 "Horrific Appearance:su",
                 "Magic Immunity:ex",
                 "Negative Energy Affinity:su",
                 "Stench:ex",
                 ])

    def test_null(self):
        t = ''
        self.assertEqual(specialparser.parseSimpleSpecial(t), [])


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
            kw = '/'.join(["%s:%s" % (k,v) for (k,v) in
                sorted(quality.kw.items())])
            ret.append("kw={kw} type={q.type} name={q.name}".format(
                kw=kw, q=quality))
        return '\n'.join(ret)

    def test_empty(self):
        self.assertEqual(specialparser.parseSpecialQualities("-"), [])

    def test_immunity(self):
        """
        Immunity Specials can parse
        """
        self.compare("Immunity to sleep and paralysis, electricity immunity",
                "kw=what:sleep type=immunity name=Immunity\n"
                "kw=what:paralysis type=immunity name=Immunity\n"
                "kw=what:electricity type=immunity name=Immunity")

    def test_misc(self):
        """
        Miscs can be captured, and their arguments are also captured
        """
        self.compare("Distraction", "kw= type=misc name=Distraction")
        self.compare("Distraction (dc 45)", "kw=dc:45 type=misc name=Distraction")
        self.compare("Distraction (butt-monkeys)", "kw=qualifier:butt-monkeys type=misc name=Distraction")

    def test_misc(self):
        """
        Misc Specials can parse
        """
        self.compare("alternate form", "kw= type=noArgumentQuality name=alternate form")
        self.compare("All-around vision, sonic blast", 
                "kw= type=sense name=All-around vision\n"
                "kw= type=misc name=sonic blast")
        self.compare("Frightful presence", "kw= type=aura name=Frightful presence")
        self.compare("Frightful presence (dc 20)", "kw=dc:20 type=aura name=Frightful presence")
        self.compare("Spells", "kw= type=spells name=spells")
        self.compare("Spell-like abilities, spells (caster level 10)", 
                "kw= type=noArgumentQuality name=Spell-like abilities\n"
                "kw=level:10 type=spells name=spells")

    def test_breathWeapon(self):
        """
        Breath weapons get parsed
        """
        self.compare("Breath weapon", "kw= type=damaging name=Breath weapon")
        self.compare("Breath weapon (70 ft. cone of fire 24d10, DC 41), breath weapon (70 ft. cone of force 35d12, dc 50)", 
                "kw=damage:24d10/dc:41/effect:cone of fire/range:70 ft. type=damaging name=Breath weapon\n"
                "kw=damage:35d12/dc:50/effect:cone of force/range:70 ft. type=damaging name=Breath weapon")
        self.compare("Breath weapon (70 ft. prismatic spray effect, Dc 41)",
                "kw=dc:41/effect:prismatic spray effect/range:70 ft. type=damaging name=Breath weapon")

    def test_damaging(self):
        """
        Specials that cause damage can parse
        """
        self.compare("trample", "kw= type=damaging name=trample")
        self.compare("trample, triple damage",
            "kw= type=damaging name=trample\n"
            "kw= type=misc name=triple damage")
        self.compare("Rend 4d6+18", "kw=damage:4d6+18 type=damaging name=Rend")
        self.compare("Crush 2d8+13 (dc 26)", "kw=damage:2d8+13/dc:26 type=damaging name=Crush")
        self.compare("Crush 2d8+13 plus 1d6 ninjas (dc 26)",
                "kw=damage:2d8+13/dc:26/extraDamage:plus 1d6 ninjas type=damaging name=Crush")
        self.compare("Constrict 1d1+1 (arm), Constrict 2d2+2 (leg)",
                "kw=damage:1d1+1/qualifier:arm type=damaging name=Constrict\n"
                "kw=damage:2d2+2/qualifier:leg type=damaging name=Constrict")

    def test_summon(self):
        """
        Summon monsters
        """
        self.compare("Summon lesser demon of truth", "kw=what:lesser demon of truth type=summon name=Summon")


class HUGESpecialParserTest(unittest.TestCase):
    """
    Test every known Special stat against the parser
    """
    _cachedSQ = None
    _cachedSAT = None
    _cachedSAB = None

    def setUp(self):
        monsters = MONSTERS.dump()
        if self._cachedSQ is None:
            self._cachedSQ = []
            self._cachedSAT = []
            self._cachedSAB = []
            for monster in monsters:
                self._cachedSQ.append ((monster, monster.special_qualities))
                self._cachedSAT.append((monster, monster.special_attacks))
                self._cachedSAB.append((monster, monster.special_abilities))

    def doTest(self, monster, stat, parser):
        try:
            if stat:
                act = [monster.name, parser(stat) and None]
        except:
            f = traceback.format_exc(sys.exc_info()[2])
            self.assertTrue(False,
                    "{x}\n{0}\n{1}\n".format(monster.name, stat, x=f))

    def test_hugeSpecialQualities(self):
        """
        Everything.
        """
        for monster, stat in self._cachedSQ:
            self.doTest(monster, stat, specialparser.parseSpecialQualities)

    def test_hugeSpecialAbilities(self):
        """
        Everything.
        """
        for monster, stat in self._cachedSAB:
            self.doTest(monster, stat, specialparser.parseSimpleSpecial)

    def test_hugeSpecialAttacks(self):
        """
        Everything.
        """
        for monster, stat in self._cachedSAT:
            self.doTest(monster, stat, specialparser.parseSpecialQualities)

        ## specialparser.printFrequenciesOfUnknowns()

