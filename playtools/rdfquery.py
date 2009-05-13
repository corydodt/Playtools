from twisted.python import log

from rdflib.Namespace import Namespace as NS
from rdflib import RDF

from rdfalchemy import rdfSingle, rdfMultiple
from rdfalchemy.orm import mapper

from playtools import sparqly as S

from goonmill.util import RESOURCE


FAM = NS('http://goonmill.org/2007/family.n3#')
CHAR = NS('http://goonmill.org/2007/characteristic.n3#')
DICE = NS('http://goonmill.org/2007/dice.n3#')
PCCLASS = NS('http://goonmill.org/2007/pcclass.n3#')
PROP = NS('http://goonmill.org/2007/property.n3#')
SKILL = NS('http://goonmill.org/2007/skill.n3#')
FEAT = NS('http://goonmill.org/2007/feat.n3#')

DB_LOCATION = RESOURCE('rdflib.db')

class SpecialArmorClass(S.rdfsPTClass):
    """Permanent, racial modifier to armor class"""
    rdf_type = CHAR.SpecialArmorClass


class Aura(S.rdfsPTClass):
    """
    Permanent effect that extends some distance around the body of the
    creature.
    """
    rdf_type = CHAR.Aura


class SpecialAction(S.rdfsPTClass):
    """Something a creature can do besides attack"""
    rdf_type = CHAR.SpecialAction


class AttackEffect(S.rdfsPTClass):
    """Some type of damage such as cold or non-magical"""
    rdf_type = CHAR.AttackEffect


class Resistance(S.rdfsPTClass):
    """A resistance possessed by monsters"""
    rdf_type = CHAR.Resistance

    attackEffect = rdfSingle(PROP.attackEffect, range_type=CHAR.AttackEffect)
    value = rdfSingle(RDF.value)

    ## def __repr__(self):
    ##     return '<%s to %s>' % (self.__class__.__name__, self.attackEffect.label)


class Vulnerability(S.rdfsPTClass):
    """A vulnerability possessed by monsters"""
    rdf_type = CHAR.Vulnerability


class Immunity(S.rdfsPTClass):
    """An immunity possessed by monsters"""
    rdf_type = CHAR.Immunity


class Sense(S.rdfsPTClass):
    """A notable sense possessed by monsters, such as darkvision"""
    rdf_type = CHAR.Sense
    range = rdfSingle(PROP.range)


class Language(S.rdfsPTClass):
    """A language understood by monsters"""
    rdf_type = CHAR.Language


class SpecialAbility(S.rdfsPTClass):
    """A notable ability of any kind that isn't a standard combat mechanic"""
    rdf_type = CHAR.SpecialAbility


class SpecialQuality(S.rdfsPTClass):
    """A notable quality possessed by the creature that is always on"""
    rdf_type = CHAR.SpecialQuality


class CombatMechanic(S.rdfsPTClass):
    """A special combat mechanic that applies to this creature"""
    rdf_type = CHAR.CombatMechanic


class MoveMechanic(S.rdfsPTClass):
    """A special move mechanic that applies to this creature"""
    rdf_type = CHAR.MoveMechanic


class Family(S.rdfsPTClass):
    """A family of monster with shared characteristics"""
    rdf_type = CHAR.Family
    senses = rdfMultiple(PROP.sense, range_type=CHAR.Sense)
    languages = rdfMultiple(PROP.language, range_type=CHAR.Language)
    immunities = rdfMultiple(PROP.immunity, range_type=CHAR.Immunity)
    resistances = rdfMultiple(PROP.resistance, range_type=CHAR.Resistance)
    vulnerabilities = rdfMultiple(PROP.vulnerability,
            range_type=CHAR.Vulnerability)
    specialAbilities = rdfMultiple(PROP.specialAbility,
            range_type=CHAR.SpecialAbility)
    specialQualities = rdfMultiple(PROP.specialQuality,
            range_type=CHAR.SpecialQuality)
    combatMechanics = rdfMultiple(PROP.combatMechanic,
            range_type=CHAR.CombatMechanic)


class Ability(S.rdfsPTClass):
    """An ability score"""
    rdf_type = CHAR.AbilityScore


class SkillSynergy(S.rdfsPTClass):
    """A skill synergy"""
    rdf_type = CHAR.SkillSynergy

    bonus = rdfSingle(PROP.bonus)
    synergyComment = rdfSingle(PROP.synergyComment)
    otherSkill = rdfSingle(PROP.fromSkill, range_type=CHAR.Skill)


class Skill(S.rdfsPTClass):
    """A skill usable by monsters, such as Diplomacy"""
    rdf_type = CHAR.Skill

    keyAbility = rdfSingle(PROP.keyAbility, range_type=CHAR.AbilityScore)
    synergy = rdfMultiple(PROP.synergy, range_type=CHAR.SkillSynergy)
    additional = rdfSingle(PROP.additional)
    epicUse = rdfSingle(PROP.epicUse)
    skillAction = rdfSingle(PROP.skillAction)
    skillCheck = rdfSingle(PROP.skillCheck)
    tryAgainComment = rdfSingle(PROP.tryAgainComment)
    untrained = rdfSingle(PROP.untrained)


class Feat(S.rdfsPTClass):
    """A feat usable by monsters, such as Weapon Focus"""
    rdf_type = CHAR.Feat
    stackable = S.rdfIsInstance(CHAR.StackableFeat)
    canTakeMultiple = S.rdfIsInstance(CHAR.CanTakeMultipleFeat)
    epic = S.rdfIsInstance(CHAR.EpicFeat)
    psionic = S.rdfIsInstance(CHAR.PsionicFeat)
    isArmorClassFeat = S.rdfIsInstance(CHAR.ArmorClassFeat)
    isAttackOptionFeat = S.rdfIsInstance(CHAR.AttackOptionFeat)
    isSpecialActionFeat = S.rdfIsInstance(CHAR.SpecialActionFeat)
    isRangedAttackFeat = S.rdfIsInstance(CHAR.RangedAttackFeat)
    isSpeedFeat = S.rdfIsInstance(CHAR.SpeedFeat)

    additional = rdfSingle(PROP.additional)
    benefit = rdfSingle(PROP.benefit)
    choiceText = rdfSingle(PROP.choiceText)
    prerequisiteText = rdfSingle(PROP.prerequisiteText)
    noFeatComment = rdfSingle(PROP.noFeatComment)

mapper()

def needDatabase(f):
    """
    If the database is not loaded yet, load it
    """
    def inner(*a, **kw):
        if db is None:
            log.msg("Opening rdf database", system="rdfquery")
            openDatabase()
        return f(*a, **kw)
    return inner

@needDatabase
def allFamilies():
    return db.allFamilies()

@needDatabase
def allSpecialAC():
    return db.allSpecialAC()

@needDatabase
def allSpecialActions():
    return db.allSpecialActions()

@needDatabase
def allAuras():
    return db.allAuras()


class SRDTriplesDatabase(S.TriplesDatabase):
    def allFamilies(self):
        ret = {}
        for family in Family.ClassInstances():
            ret[family.label] = family

        return ret
                
    def allAuras(self):
        ret = {}
        for aura in Aura.ClassInstances():
            ret[aura.label.lower()] = aura

        return ret

    def allSpecialAC(self):
        ret = {}
        for armor in SpecialArmorClass.ClassInstances():
            ret[armor.label.lower()] = armor

        return ret

    def allSpecialActions(self):
        ret = {}
        for action in SpecialArmorClass.ClassInstances():
            ret[action.label.lower()] = action

        return ret


db = None

def openDatabase():
    """
    Open the database. Has the side-effect of making the db available at the
    module level.
    """
    global db
    db = SRDTriplesDatabase()
    db.open(DB_LOCATION)

    # initialize rdfalchemy mapper
    S.rdfsPTClass.db = db.graph

    return db

