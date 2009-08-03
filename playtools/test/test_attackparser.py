"""
Test for the parsing of attack groups into attack forms and on down
"""

from twisted.trial import unittest

from playtools.parser import attackparser
from playtools import fact

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class AttackParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
    def formatAttackForm(self, form):
        bonus='/'.join(['%+d'%(b,) for b in form.bonus])
        return ('{f.count}|{f.weapon}|{bonus}|{f.damage}|{f.crit}|'
                '{extraDamage}|{f.type}|{f.touch}|{f.rangeInformation}').format(
                f=form, bonus=bonus, extraDamage="/".join(form.extraDamage))

    def assertAttackGroup(self, group, expected):
        for form, wanted in zip(group.attackForms, expected):
            self.assertEqual(self.formatAttackForm(form), wanted)
 
    def test_regular(self):
        """
        Plain jane attacks can parse
        """
        F = self.formatAttackForm
        t1 = "Bite +104 (25d10+24) melee" 
        parsed = attackparser.parseAttacks(t1)[0][0]
        self.assertAttackGroup(parsed, ["1|Bite|+104|25d10+24|20||melee||"])

        t2 = "Bite +86 (4d8+28/19-20) melee, 2 Claws +86 (4d6+14/19-20) melee"
        parsed = attackparser.parseAttacks(t2)[0][0]
        self.assertAttackGroup(parsed, ["1|Bite|+86|4d8+28|19-20||melee||",
            "2|Claws|+86|4d6+14|19-20||melee||"])

    def test_rangeInfo(self):
        """
        When ranges are given in the attack, they get captured
        """
        t = "electricity ray +35 ranged touch (10d6 electricity), 6 spikes +30 ranged (2d6+12) (120 ft. range increment)"
        parsed = attackparser.parseAttacks(t)[0][0]
        self.assertAttackGroup(parsed, [
                "1|electricity ray|+35|10d6 electricity|20||ranged|touch|",
                "6|spikes|+30|2d6+12|20||ranged||120 ft. range increment"
                ])

    def test_damageType(self):
        """
        Special types of damage show up in the damage spot
        """
        t0 = "mental attack +4 melee touch (eat thoughts)"
        parsed = attackparser.parseAttacks(t0)[0][0]
        self.assertAttackGroup(parsed,
                ["1|mental attack|+4|eat thoughts|20||melee|touch|"])

        t1 = "2 touches +49 (2d6 Con drain/19-20) melee touch, eye ray +30 (negative level damage/19-20) ranged touch"
        parsed = attackparser.parseAttacks(t1)[0][0]
        self.assertAttackGroup(parsed,
                ["2|touches|+49|2d6 Con drain|19-20||melee|touch|",
                 "1|eye ray|+30|negative level damage|19-20||ranged|touch|"])

        t2 = "6 bites +4 melee (1) and spittle +4 ranged touch (1d4 acid (plus blindness))"
        parsed = attackparser.parseAttacks(t2)[0][0]
        self.assertAttackGroup(parsed,
                ["6|bites|+4|1|20||melee||",
                 "1|spittle|+4|1d4 acid|20|plus blindness|ranged|touch|"])

    def test_damageProductions(self):
        """
        The delicate productions for damage (with and without extra, with and
        without type, no dice) are all functioning correctly
        """
        def test(s, production, expected):
            group = attackparser.AttackGroup()
            group.attackForms = [attackparser.AttackForm()]
            attackparser.parseAttacks(s, production=production, probe=[group])
            self.assertAttackGroup(group, expected)

        t0 = "1d8"
        test(t0, "diceOnly", ["1|||1d8|20||None||"])
        test(t0, "damage", ["1|||1d8|20||None||"])
        t0b = "1d8/19-20"
        test(t0b, "diceOnly", ["1|||1d8|19-20||None||"])
        test(t0b, "damage", ["1|||1d8|19-20||None||"])

        t1 = "4d8+8 plus spell suck"
        test(t1, "diceAndExtraDamage", ["1|||4d8+8|20|plus spell suck|None||"])
        test(t1, "damage", ["1|||4d8+8|20|plus spell suck|None||"])
        t1b = "4d8+8/19-20 plus spell suck"
        test(t1b, "diceAndExtraDamage", ["1|||4d8+8|19-20|plus spell suck|None||"])
        test(t1b, "damage", ["1|||4d8+8|19-20|plus spell suck|None||"])

        t2b = "1d4 acid/19-20 (plus blindness)"
        test(t2b, "diceTypeAndExtraDamage", ["1|||1d4 acid|19-20|plus blindness|None||"])
        test(t2b, "damage", ["1|||1d4 acid|19-20|plus blindness|None||"])
        t2 = "1d4 acid (plus blindness)"
        test(t2, "diceTypeAndExtraDamage", ["1|||1d4 acid|20|plus blindness|None||"])
        test(t2, "damage", ["1|||1d4 acid|20|plus blindness|None||"])

        t3 = "1d6 Str"
        test(t3, "diceAndTypeDamage", ["1|||1d6 Str|20||None||"])
        test(t3, "damage", ["1|||1d6 Str|20||None||"])
        t3b = "1d6 Str/19-20"
        test(t3b, "diceAndTypeDamage", ["1|||1d6 Str|19-20||None||"])
        test(t3b, "damage", ["1|||1d6 Str|19-20||None||"])

        t4 = "energy drain"
        test(t4, "nonDiceDamage", ["1|||energy drain|20||None||"])
        test(t4, "damage", ["1|||energy drain|20||None||"])
        t4b = "energy drain/19-20"
        test(t4b, "nonDiceDamage", ["1|||energy drain|19-20||None||"])
        test(t4b, "damage", ["1|||energy drain|19-20||None||"])

    def test_extraDamage(self):
        """
        Attacks that describe extra damage have that damage parsed
        """
        t0 = "4 claws +56 (2d6+16/19-20 (+1d6 on critical hit)) melee"
        parsed = attackparser.parseAttacks(t0)[0][0]
        self.assertAttackGroup(parsed, 
                ["4|claws|+56|2d6+16|19-20|+1d6 on critical hit|melee||"])

        t3 = "tail slap +9 melee (2d6+1 plus 1d6 fire)"
        parsed = attackparser.parseAttacks(t3)[0][0]
        self.assertAttackGroup(parsed, ["1|tail slap|+9|2d6+1|20|plus 1d6 fire|melee||"])

        t1 = "Spear +11/+6 melee (1d8+3/x3 plus 1d6 fire) and tail slap +9 melee (2d6+1 plus 1d6 fire)"
        parsed = attackparser.parseAttacks(t1)[0][0]
        self.assertAttackGroup(parsed, ["1|Spear|+11/+6|1d8+3|x3|plus 1d6 fire|melee||",
            "1|tail slap|+9|2d6+1|20|plus 1d6 fire|melee||"])

        t2 = "plus6 keen longsword of binding +46/+41/+36/+31 (1d8+27/17-20 (plus 1d6 plus binding)) melee"
        parsed = attackparser.parseAttacks(t2)[0][0]
        self.assertAttackGroup(parsed, 
                ["1|plus6 keen longsword of binding|+46/+41/+36/+31|1d8+27|17-20|plus 1d6 plus binding|melee||"])

    def test_multipleGroups(self):
        """
        Monsters with a combination of ranged and melee attacks can parse
        """
        t = "Morningstar +5 melee (1d8+2) or javelin +3 ranged (1d6+2)"
        parsed = attackparser.parseAttacks(t)[0]

        expected0 = ["1|Morningstar|+5|1d8+2|20||melee||"]
        self.assertAttackGroup(parsed[0], expected0)

        expected1 = ["1|javelin|+3|1d6+2|20||ranged||"]
        self.assertAttackGroup(parsed[1], expected1)

    def test_empty(self):
        """
        No ("-") attack still parses
        """
        t = "-"
        parsed = attackparser.parseAttacks(t)[0]
        self.assertEqual(parsed, [])


class HUGEAttackParserTest(unittest.TestCase):
    """
    Test every known attack stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            # we aren't actually making any assertions about attacks except
            # that they can be processed.  The "exp" construction is here so
            # that the assertEqual at the end will have a string to tell us
            # *which* monster failed, if one does.
            exp = [monster.name, None]

            stat = monster.full_attack

            # get('name') as a proxy for checking that the monster actually
            # loaded ok.
            try:
                act = [monster.name, attackparser.parseAttacks(stat) and None]
                self.assertEqual(exp, act)
            except Exception, e:
                print '!!!!', monster.name, stat
                raise


