"""
Test access to the triplestore
"""

import unittest
import string

import re

from .. import rdfquery

import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

class RDFQueryTestCase(unittest.TestCase):
    def setUp(self):
        if rdfquery.db is None:
            rdfquery.openDatabase()

    def test_schemaAccess(self):
        """
        I can access the schema at all
        """
        fireResistance = rdfquery.Immunity(rdfquery.CHAR.fire)

    def test_feat(self):
        """
        Verify that attributes of the feat triples are accessible
        """
        heavy = feat('armorProficiencyHeavy')

        exp = '.*Armor Proficiency \(medium\).*'
        act = heavy.prerequisiteText

        self.failIfEqual(re.match(exp, str(act)), None, "%s != %s" % (exp, act))
        self.assertEqual(heavy.stackable, False)

    def test_skill(self):
        """
        Verify that attributes of the skill triples are accessible
        """
        cha = rdfquery.Ability(rdfquery.CHAR.cha)
        self.assertEqual(str(cha.label), 'Cha')

        dipl = skill('diplomacy')

        self.assertEqual(str(dipl.keyAbility.label), 'Cha')
        # TODO - should be able to get an integer here straight from the API,
        # oh well
        self.assertEqual(int(dipl.synergy[0].bonus), 2)

    def test_family(self):
        """
        Verify that attributes of the family triples are accessible
        """
        F = family
        self.assertEqual(len(F('devil').languages), 3)

        mechs = sorted(F('ooze').combatMechanics)
        self.assertEqual(str(mechs[0].label), 'Not subject to critical hits')

        sqs = sorted(F('undead').specialQualities)
        self.assertEqual(str(sqs[0].comment), 
            'Cannot be raised or resurrected.')
        self.assertEqual(len(F('construct').combatMechanics), 8)

        senses = sorted(F('fey').senses)
        self.assertEqual(str(senses[0].label), 'Low-Light Vision')

    def test_resistancesAndImmunities(self):
        """
        I can read off resistances and immunities from a family
        """
        angel = family('angel')

        resl = sorted(pluck(angel.resistances, 'attackEffect', 'label'))
        resv = sorted(pluck(angel.resistances, 'value'))
        self.assertEqual(resl, ['Electricity', 'Fire'])
        self.assertEqual(resv, [10, 10])

        imml = sorted(pluck(angel.immunities, 'label'))
        self.assertEqual(imml, ['Acid', 'Cold', 'Petrification'])

def skill(k):
    return rdfquery.Skill(getattr(rdfquery.SKILL, k))
def feat(k):
    return rdfquery.Feat(getattr(rdfquery.FEAT, k))
def family(k):
    return rdfquery.Family(getattr(rdfquery.FAM, k))

def pluck(items, *attrs):
    """
    For each item return getattr(item, attrs[0]) recursively down to the
    furthest-right attribute in attrs.
    """
    a = attrs[0]
    rest = attrs[1:]
    these = (getattr(o,a) for o in items)
    if len(rest) == 0:
        return these
    else:
        return pluck(these, *rest)
