"""
We shall be able to pull facts about the srd35 system out using the API
"""

import re
import os
from itertools import count

from twisted.trial import unittest

from .. import fact
from ..interfaces import IIndexable
from playtools.plugins import d20srd35
from playtools.common import featNs as FEAT, monsterNs as MONSTER, C
from playtools.test.pttestutil import pluck

import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

SRD = fact.systems['D20 SRD']

class SRD35TestCase(unittest.TestCase):
    """
    Pull out the facts
    """
    def test_loadReferenceURLs(self):
        """
        The reference URLs refer to the correct file, relative to the plugins
        directory
        """
        refs = d20srd35.loadReferenceURLs()
        dir = os.path.dirname(d20srd35.__file__)
        self.assertTrue(os.path.isfile(dir + '/monster/' + refs['drow1stLevelWarrior'][1]))
        self.assertEqual(refs['drow1stLevelWarrior'], 
            ['http://www.d20srd.org/srd/monsters/elf.htm',
                'monstertext/elf.htm'])

    def test_lookupSQL(self):
        """
        Spells and Monsters are available for lookup (the SQL aka Storm facts)
        """
        monsters = SRD.facts['monster']
        spells = SRD.facts['spell']

        def test(n,k,s):
            self.assertEqual(k.lookup(n).name, s)

        test(10, monsters, u'Behemoth Eagle')
        test(10, spells, u'Surelife')

    def test_lookupRDF(self):
        """
        The RDF facts are available for lookup
        """
        families = SRD.facts['family']
        auras = SRD.facts['aura']
        skills = SRD.facts['skill']
        feats = SRD.facts['feat']
        specialACs = SRD.facts['specialAC']
        specialActions = SRD.facts['specialAction']

        def test(n,k,s):
            thing = k.lookup(n)
            self.assertEqual(unicode(thing.label), s)

        test(u'http://goonmill.org/2007/family.n3#devil', families, u'Devil')
        test(u'http://goonmill.org/2007/specialAbility.n3#nullTimeField', auras, u'Null Time Field')
        test(u'http://goonmill.org/2007/skill.n3#appraise', skills, u'Appraise')
        test(u'http://goonmill.org/2007/feat.n3#abilityFocus', feats, u'Ability Focus')
        test(u'http://goonmill.org/2007/specialAbility.n3#deflectingForce', specialACs, u'Deflecting Force')
        test(u'http://goonmill.org/2007/specialAbility.n3#mucusCloud', specialActions, u'Mucus Cloud')

    def test_thingLists(self):
        """
        Verify that we are retrieving the right number of things from the
        database with our dump methods

        Somewhat repeats the tests in test_fact in the absence of any other
        test fixture to test that.
        """
        monsters = SRD.facts['monster']
        spells = SRD.facts['spell']
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
        spells = SRD.facts['spell']
        cswm = spells.lookup(205)
        self.assertEqual(u'http://www.d20srd.org/srd/spells/cureSeriousWoundsMass.htm',
                d20srd35.srdReferenceURL(cswm))
        animusBlast = spells.lookup(15)
        self.assertEqual(u'http://www.d20srd.org/srd/epic/spells/animusBlast.htm',
                d20srd35.srdReferenceURL(animusBlast))

    def test_facts(self):
        """
        We can get a dict of fact domains that exist in a particular system
        """
        self.assertTrue('spell' in SRD.facts)
        self.assertTrue('monster' in SRD.facts)

    def test_schemaAccess(self):
        """
        I can access the schema at all
        """
        fireResistance = d20srd35.Immunity(d20srd35.CHAR.fire)

    def test_feat(self):
        """
        Verify that attributes of the feat triples are accessible
        """
        def tests(F):
            # test using direct sparqly access
            heavy = F('armorProficiencyHeavy')

            exp = '.*Armor Proficiency \(medium\).*'
            act = heavy.prerequisiteText

            self.failIfEqual(re.match(exp, str(act)), None, "%s !~ %s" % (exp, act))
            self.assertEqual(heavy.stackable, False)

        # test using direct sparqly access
        def direct(k):
            return d20srd35.Feat(getattr(d20srd35.FEAT, k))

        # test using fact module
        def factModule(k):
            return SRD.facts['feat'][getattr(d20srd35.FEAT, k)]

        tests(direct)
        tests(factModule)

    def test_skill(self):
        """
        Verify that attributes of the skill triples are accessible
        """
        def tests(F):
            # test using direct sparqly access
            cha = d20srd35.Ability(d20srd35.CHAR.cha)
            self.assertEqual(str(cha.label), 'Cha')

            dipl = F('diplomacy')

            self.assertEqual(str(dipl.keyAbility.label), 'Cha')
            # TODO - should be able to get an integer here straight from the API,
            # oh well
            self.assertEqual(int(dipl.synergy[0].bonus), 2)

        # test using direct sparqly access
        def direct(k):
            return d20srd35.Skill(getattr(d20srd35.SKILL, k))

        # test using fact module
        def factModule(k):
            return SRD.facts['skill'][getattr(d20srd35.SKILL, k)]

        tests(direct)
        tests(factModule)

    def test_family(self):
        """
        Verify that attributes of the family triples are accessible
        """
        def tests(F):
            self.assertEqual(len(F('devil').languages), 3)

            mechs = sorted(F('ooze').combatMechanics)
            self.assertEqual(str(mechs[0].label), 'Not subject to critical hits')

            sqs = sorted(F('undead').specialQualities)
            self.assertEqual(str(sqs[0].comment), 
                'Cannot be raised or resurrected.')
            self.assertEqual(len(F('construct').combatMechanics), 8)

            senses = sorted(F('fey').senses)
            self.assertEqual(str(senses[0].label), 'Low-Light Vision')

        # test using direct sparqly access
        def direct(k):
            return d20srd35.Family(getattr(d20srd35.FAM, k))

        # test using fact module
        def factModule(k):
            return SRD.facts['family'][getattr(d20srd35.FAM, k)]

        tests(direct)
        tests(factModule)

    def test_resistancesAndImmunities(self):
        """
        I can read off resistances and immunities from a family
        """
        # test accessing via fact module
        angel = SRD.facts['family'][d20srd35.FAM.angel]

        resl = sorted(pluck(angel.resistances, 'attackEffect', 'label'))
        resv = sorted(pluck(angel.resistances, 'value'))
        self.assertEqual(resl, ['Electricity', 'Fire'])
        self.assertEqual(resv, [10, 10])

        imml = sorted(pluck(angel.immunities, 'label'))
        self.assertEqual(imml, ['Acid', 'Cold', 'Petrification'])

    def test_indexable(self):
        """
        All collections should be indexable
        """
        for coll in SRD.facts.values():
            item = coll.dump()[0]
            self.assertTrue(IIndexable(item), "Collection %s (%s)"
                    % (coll, coll.factName))

    def test_monster(self):
        """
        Verify that attributes of the monster triples are accessible
        (Monster2)
        """
        m = SRD.facts['monster2']
        badger = m.lookup(MONSTER.badger)
        self.assertEqual(str(badger.hitDice), 'd8+2')
        self.assertEqual(pluck(badger.bonusFeats, 'feat', 'resUri'), [FEAT.track])
        self.assertEqual(pluck(badger.epicFeats, 'feat', 'resUri'), [])

        gorilla = m.lookup(MONSTER.behemothGorilla)
        self.assertEqual(sorted(pluck(gorilla.acFeats, 'feat', 'resUri')),
                [FEAT.dodge, FEAT.mobility])
        self.assertEqual(pluck(gorilla.epicFeats, 'feat', 'resUri'),
                [FEAT.epicToughness])

        # listen is a descriptor that gets the value of that skill
        aboleth = m.lookup(MONSTER.aboleth)
        self.assertEqual(aboleth.listen.value, 16)

        # attack is a descriptor that gets the first attack from fullAttack
        def fmt(attack):
            melee = "melee" if attack.isMelee else "ranged"
            bonus = '/'.join(["%+d" % (n,) for n in attack.bonus])
            return ("{melee}|{x.label}|{x.count}|{bonus}|"
                    "{x.damage}|{x.critical}|{x.extraDamage}".format(
                        x=attack, melee=melee, bonus=bonus)
                    )

        cloudGiant = m.lookup(MONSTER.cloudGiant)
        singleAttack = cloudGiant.attack
        self.assertEqual(
                fmt(cloudGiant.attack),
                "melee|Gargantuan morningstar|1|+22|4d6+18|None|None"
                )

        winterwight = m.lookup(MONSTER.winterwight)
        singleAttack = winterwight.attack
        self.assertEqual(
                fmt(winterwight.attack),
                "melee|claws|1|+40|3d8+21|19-20|plus blight-fire, +1d6 on critical hit"
                )

        # abilities, saves, treasures: associative types
        self.assertEqual(winterwight.abilities['strength'], 52)
        self.assertEqual(winterwight.treasures['goods'],
            C.standardTreasure)
        self.assertEqual(winterwight.saves['reflex'], 18)
        
        # flatFootedAC and touchAC: descriptors that compute armor value for
        # special circumstances
        fleshColossus = m.lookup(MONSTER.fleshColossus)
        self.assertEqual(fleshColossus.touchAC, 20)
        self.assertEqual(fleshColossus.flatFootedAC, 45)

        forceDragon = m.lookup(MONSTER.forceDragonAdult)
        fdAbilities = [x.name for x in forceDragon.specialAbilities]

        # low-light vision is only found in the dragon type, and not found in
        # the force dragon's particular ability list. use this to test that
        # inheriting abilities is working right
        self.assertTrue('Low-Light Vision' in fdAbilities)

        self.assertTrue('Deflecting Force' in fdAbilities)
        self.assertEqual(forceDragon.specialAC, u"Deflecting Force")
        self.assertTrue('Damage Reduction' in fdAbilities)
        self.assertEqual(forceDragon.damageReduction, {'xx':xx})
        self.assertTrue('Spell Resistance' in fdAbilities)
        self.assertEqual(forceDragon.spellResistance, 39)
        self.assertTrue('Caster Level' in fdAbilities)
        self.assertEqual(forceDragon.casterLevel, 18)
        self.assertTrue('Fast Healing' in fdAbilities)
        self.assertEqual(forceDragon.fastHealing, xx)
        self.assertTrue('Regeneration' in fdAbilities)
        self.assertEqual(forceDragon.regeneration, xx)
        self.assertTrue('Aura of Good' in fdAbilities)
        self.assertTrue('Aura of Courage' in fdAbilities)
        self.assertEqual(forceDragon.auras, [u'good', u'courage'])
        self.assertTrue('Immunity to xx' in fdAbilities)
        self.assertTrue('Immunity to yy' in fdAbilities)
        self.assertEqual(forceDragon.immunities, [xx, yy])
        self.assertTrue('Vulnerability to xx' in fdAbilities)
        self.assertTrue('Vulnerability to yy' in fdAbilities)
        self.assertEqual(forceDragon.vulnerabilities, [xx, yy])
        self.assertTrue('XX resistance xx' in fdAbilities)
        self.assertEqual(forceDragon.resistances, {'xx':xx})
        self.assertTrue('xx' in fdAbilities)
        self.assertEqual(forceDragon.senses, {'xx':xx})
        self.assertEqual([x.name for x in forceDragon.spellLikeAbilities], ['xx','xx'])
        self.assertEqual([x.name for x in forceDragon.extraordinaryAbilities], ['xx','xx'])
        self.assertEqual([x.name for x in forceDragon.supernaturalAbilities], ['xx','xx'])
        self.assertEqual([x.name for x in forceDragon.specialAttacks], ['xx','xx'])

    def test_bonusFeat(self):
        """
        The bonus feat property can be used to access the bonus feats
        """
        MF = d20srd35.MonsterFeat
        acro = MF(); acro.coreFeat = FEAT.acrobatic
        agile = MF(); agile.coreFeat = FEAT.agile
        zone = MF(); zone.coreFeat = FEAT.zoneOfAnimation
        zone.isBonusFeat = True
        sunder = MF(); sunder.coreFeat = FEAT.focusedSunder
        sunder.isBonusFeat = True
        _feats = (acro, agile, zone, sunder)

        class Tester(object):
            bonusFeats = d20srd35.BonusFeatFilter("bonusFeats")
            feats = _feats

        t = Tester()
        self.assertEqual(pluck(list(t.bonusFeats), 'coreFeat'),
                [FEAT.zoneOfAnimation, FEAT.focusedSunder])


class CachingDescriptorTest(unittest.TestCase):
    def test_basicAccess(self):
        """
        I can reach an attribute through the descriptor
        """
        class TestDescriptor(d20srd35.CachingDescriptor):

            def get(self, instance, owner):
                return 1

        class C(object):
            x = TestDescriptor('x')

        c = C()
        self.assertEqual(c.x, 1)

    def test_cached(self):
        """
        When a value has been cached, return the cached value instead of the
        computed one
        """
        counter = count()
        class TestDescriptor(d20srd35.CachingDescriptor):
            def get(self, instance, owner):
                return counter.next()

        class C(object):
            x = TestDescriptor('x')
            y = TestDescriptor('y')

        c = C()
        self.assertEqual(c.x, 0)
        counter.next()
        self.assertEqual(c.x, 0)
        self.assertEqual(c.y, 2)
        counter.next()
        self.assertEqual(c.y, 2)
