"""
Test for the parsing of armorclass
"""

from twisted.trial import unittest
from playtools.parser import armorclassparser
from playtools import fact

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']


DEFAULT = object()

class ArmorClassParserTest(unittest.TestCase):
    def check(self, ac, expected):
        parsed = armorclassparser.parseArmor(ac)[0]
        others = []
        for o in parsed.otherArmor:
            others.append("{0}({1})".format(*o))
        other = '/'.join(others)
        shield = "{0}({1})".format(*parsed.shield) if parsed.shield[0] else ""
        body = "{0}({1})".format(*parsed.body) if parsed.body[0] else ""
        q = "" if parsed.qualifier is None else parsed.qualifier
        rep = ("v={x.value} dex={x.dexBonus} s={x.size} nat={x.natural} "
               "def={x.deflection} oth={other} b={body} sh={shield} "
               "to={x.touch} ff={x.flatFooted} q={q}"
            ).format(x=parsed, other=other, body=body, shield=shield, q=q)
        self.assertEqual(rep, expected)

    def test_boring(self):
        """
        Normal armor with only standard numbers
        """
        t1 = "55 (-8 size, +13 Dex, +40 natural), touch 15, flat-footed 42"
        self.check(t1, "v=55 dex=13 s=-8 nat=40 def=0 oth= b= sh= to=15 ff=42 q=")
        t2 = "8 (-5 Dex, +3 natural), touch 5, flat-footed 8"
        self.check(t2, "v=8 dex=-5 s=0 nat=3 def=0 oth= b= sh= to=5 ff=8 q=")
        t3 = "0 (-2 Dex, -8 size), touch 0, flat-footed 0"
        self.check(t3, "v=0 dex=-2 s=-8 nat=0 def=0 oth= b= sh= to=0 ff=0 q=")
        t4 = "16 (+6 natural), touch 10, flat-footed 16"
        self.check(t4, "v=16 dex=0 s=0 nat=6 def=0 oth= b= sh= to=10 ff=16 q=")
        t5 = "102 (-8 size, +26 deflection, +74 natural), touch 28, flat-footed 102"
        self.check(t5, "v=102 dex=0 s=-8 nat=74 def=26 oth= b= sh= to=28 ff=102 q=")

    def test_armorOption(self):
        """
        ArmorClasses with more than one possibility
        """
        # Ghaele
        t = "25 (+1 Dex, +14 natural), touch 11, flat-footed 24, or 14 (+1 Dex, +3 deflection), touch 14, flat-footed 13"
        self.check(t, "v=25 dex=1 s=0 nat=14 def=3 oth= b= sh= to=14 ff=13 q=/v=14...")

    def test_splat(self):
        """
        Splats that appear get noted
        """
        t1 = "16 (+4 size, +2 Dex*), touch 16, flat-footed 14"
        self.check(t1, "v=16 dex=2 s=4 nat=0 def=0 oth= b= sh= to=16 ff=14 q=*")

    def test_otherArmor(self):
        """
        Weird crap like insight and haste get parsed correctly
        """
        t1 = "50 (-1 size, +7 Dex, +11 deflection, +23 insight), touch 50, flat-footed 43"
        self.check(t1, "v=50 dex=7 s=-1 nat=0 def=11 oth=23(insight) b= sh= to=50 ff=43 q=")
        t2 = "70 (-2 size, +30 natural, +20 insight, +12 armor [+5 half plate]), touch 28, flat-footed 70"
        self.check(t2, "v=70 dex=0 s=-2 nat=30 def=0 oth=20(insight) b=12(armor [+5 half plate]) sh= to=28 ff=70 q=")
        t3 = "45 (-8 size, -2 Dex, +25 natural, +20 profane), touch 20, flat-footed 45"
        self.check(t3, "v=45 dex=-2 s=-8 nat=25 def=0 oth=20(profane) b= sh= to=20 ff=45 q=")
        t5 = "42 (-2 size, +4 Dex, +26 natural, +4 haste), touch 16, flat-footed 38"
        self.check(t5, "v=42 dex=4 s=-2 nat=26 def=0 oth=4(haste) b= sh= to=16 ff=38 q=")
        t6 = "16 (+1 size, +1 Dex, +4 inertial armor), touch 12, flat-footed 15"
        self.check(t6, "v=16 dex=1 s=1 nat=0 def=0 oth= b=4(inertial armor) sh= to=12 ff=15 q=")
        t7 = "47 (+4 Dex, +8 bracers, +3 ring, +2 amulet, +20 insight), touch 39, flat-footed 43"
        self.check(t7, "v=47 dex=4 s=0 nat=0 def=0 oth=3(ring)/2(amulet)/20(insight) b=8(bracers) sh= to=39 ff=43 q=")
        t8 = "51 (+4 size, +3 Dex, +5 natural, +8 bracers of armor, +2 ring of protection, +21 insight), touch 38, flat-footed 48"
        self.check(t8, "v=51 dex=3 s=4 nat=5 def=0 oth=2(ring of protection)/21(insight) b=8(bracers of armor) sh= to=38 ff=48 q=")

    def test_bodyOrShield(self):
        """
        Body armor or shield get parsed correctly
        """
        t1 = "26 (+2 Dex, +3 natural, +6 +2 mithral chain shirt, +5 +3 heavy shield), touch 12, flat-footed 24"
        self.check(t1, "v=26 dex=2 s=0 nat=3 def=0 oth= b=6(+2 mithral chain shirt) sh=5(+3 heavy shield) to=12 ff=24 q=")
        t2 = "17 (+1 Dex, +3 natural, +2 leather armor, +1 light wooden shield), touch 11, flat-footed 16"
        self.check(t2, "v=17 dex=1 s=0 nat=3 def=0 oth= b=2(leather armor) sh=1(light wooden shield) to=11 ff=16 q=")


class HUGEArmorClassParserTest(unittest.TestCase):
    """
    Test every known armorclass stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            # we aren't actually making any assertions about armorclasses except
            # that they can be processed.  The "exp" construction is here so
            # that the assertEqual at the end will have a string to tell us
            # *which* monster failed, if one does.
            exp = [monster.name, None]

            stat = monster.armor_class

            # get('name') as a proxy for checking that the monster actually
            # loaded ok.
            act = [monster.name, armorclassparser.parseArmor(stat) and None]
            self.assertEqual(exp, act)

