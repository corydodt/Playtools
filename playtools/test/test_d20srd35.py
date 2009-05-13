"""
We shall be able to pull facts about the srd35 system out using the API
"""

import unittest
import string
import re

from .. import fact
from playtools.plugins import d20srd35

import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)


class SRD35TestCase(unittest.TestCase):
    """
    Pull out the facts
    """
    def setUp(self):
        self.srd = fact.systems['D20 SRD']

    def test_lookup(self):
        """
        Spells and Monsters are available for lookup
        """
        srd = self.srd
        monsters = srd.facts['monster']
        spells = srd.facts['spell']

        def test(n,k,s):
            self.assertEqual(k.lookup(n).name, s)

        test(10, monsters, u'Behemoth Eagle')
        test(10, spells, u'Surelife')

    def test_thingLists(self):
        """
        Verify that we are retrieving the right number of things from the
        database with our dump methods

        Somewhat repeats the tests in test_fact in the absence of any other
        test fixture to test that.
        """
        srd = self.srd
        monsters = srd.facts['monster']
        spells = srd.facts['spell']
        mdump = monsters.dump()
        sdump = spells.dump()
        self.assertEqual(len(mdump), 681)
        self.assertEqual(len(sdump), 699)
        self.assertEqual(monsters[10].name, u'Behemoth Eagle')
        self.assertEqual(spells[10].name, u'Surelife')

    def test_srdReferenceURL(self):
        """
        The srdReferenceURL utility method returns a good URL into
        www.d20srd.org for a given item
        """
        srd = self.srd
        spells = srd.facts['spell']
        cswm = spells.lookup(205)
        self.assertEqual('http://www.d20srd.org/srd/spells/cureSeriousWoundsMass.htm',
                d20srd35.srdReferenceURL(cswm))
        animusBlast = spells.lookup(15)
        self.assertEqual('http://www.d20srd.org/srd/epic/spells/animusBlast.htm',
                d20srd35.srdReferenceURL(animusBlast))

    def test_facts(self):
        """
        We can get a dict of fact domains that exist in a particular system
        """
        self.assertTrue('spell' in self.srd.facts)
        self.assertTrue('monster' in self.srd.facts)

    def test_schemaAccess(self):
        """
        I can access the schema at all
        """
        fireResistance = d20srd35.Immunity(d20srd35.CHAR.fire)

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
        cha = d20srd35.Ability(d20srd35.CHAR.cha)
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
    return d20srd35.Skill(getattr(d20srd35.SKILL, k))

def feat(k):
    return d20srd35.Feat(getattr(d20srd35.FEAT, k))

def family(k):
    return d20srd35.Family(getattr(d20srd35.FAM, k))

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
