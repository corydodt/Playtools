"""
The game system based on the D20 SRD (version 3.5)
"""
import re

from zope.interface import implements, Attribute

from twisted.plugin import IPlugin

from storm import locals as SL

from playtools.interfaces import (IRuleSystem, IRuleCollection,
    IIndexable, IRuleFact)
from playtools.util import RESOURCE
from playtools import globalRegistry, sparqly as S
from playtools.search import textFromHtml
from playtools.common import FAM, P as PROP, C as CHAR, skillNs as SKILL, featNs as FEAT
from playtools.test.pttestutil import TODO

from rdflib.Namespace import Namespace as NS
from rdflib import RDF

from rdfalchemy import rdfSingle, rdfMultiple, rdfList
from rdfalchemy.orm import mapper


from d20srd35config import SQLPATH, RDFPATH

RDFSNS = S.RDFSNS

DICE = NS('http://goonmill.org/2007/dice.n3#')
PCCLASS = NS('http://goonmill.org/2007/pcclass.n3#')


class D20SRD35System(object):
    """
    Game system based on the System Reference Document (v3.5) found
    at http://www.d20srd.org/
    """
    implements (IRuleSystem, IPlugin)
    name = "D20 SRD"
    version = "3.5"
    searchIndexPath = RESOURCE("plugins/srd35-index")
    #
    def __init__(self):
        self.facts = {}

d20srd35 = D20SRD35System()


# the d20srd databases are essentially static and permanent, so just open them here.
STORE = SL.Store(SL.create_database('sqlite:' + SQLPATH))
RDFDB = S.TriplesDatabase()
RDFDB.open(RDFPATH)
# initialize rdfalchemy mapper
S.rdfsPTClass.db = RDFDB.graph



## SQL/Storm-based facts
## SQL/Storm-based facts
## SQL/Storm-based facts

class IStormFact(IRuleFact):
    """
    The SRD/SQL facts typically all have these special attributes, useful for
    various reasons.
    """
    full_text = Attribute("full_text")
    name = Attribute("name")
    id = Attribute("id")


class IndexableStormFact(object):
    """
    Trivial layer over facts that are objects in the SRD/SQL, all of which
    have full_text, id and name.
    """
    implements(IIndexable)
    __used_for__ = IStormFact

    SLASHRX = re.compile(r'\\([n"])')

    def __init__(self, fact):
        self.fact = fact
        _ft = re.sub(self.SLASHRX, self.repSlash, fact.full_text)
        self.text = textFromHtml(_ft)
        self.uri = fact.id
        self.title = fact.name

    @staticmethod
    def repSlash(m):
        """
        Clean up bonus slashes inside the escaped raw html in storm fact texts
        """
        if m.group(1) == 'n':
            return '\n'
        return m.group(1)

# Use IndexableStormFact as an adapter for stormfacts to convert them to
# IIndexable
globalRegistry.register([IStormFact], IIndexable, '', IndexableStormFact)


class StormFactCollection(object):
    """
    A collection of RuleFacts that are Storm objects, so we can look them up
    or dump them.
    """
    implements(IRuleCollection, IPlugin)
    system = D20SRD35System
    def __init__(self, factClass, factName):
        factClass.collection = self
        self.klass = factClass
        self.factName = factName

    def __getitem__(self, key):
        ret = self.lookup(key)
        if not ret:
            raise KeyError(key)
        return ret

    def dump(self):
        """
        All instances of the factClass
        """
        return list(STORE.find(self.klass))

    def lookup(self, idOrName):
        """
        Implement the dual-interpretation logic for "idOrName" to look
        up an object from the database by id or by name.  Naturally
        this requires the table have a 'name' column.

        @return an instance of the table-mapped class, e.g. Monster, Spell,
        Feat or Skill
        """
        try:
            id = int(idOrName)
            thing = STORE.find(self.klass, self.klass.id==id).one()
            if thing is not None:
                return thing
        except ValueError:
            pass
        return STORE.find(self.klass, self.klass.name==idOrName).one()


class Monster(object):
    """A Monster mapped from the db"""
    implements(IStormFact)

    __storm_table__ = 'monster'

    collection = None

    id = SL.Int(primary=True)                #
    name = SL.Unicode()
    family = SL.Unicode()
    altname = SL.Unicode()
    size = SL.Unicode()
    type = SL.Unicode()
    descriptor = SL.Unicode()
    hit_dice = SL.Unicode()
    initiative = SL.Unicode()
    speed = SL.Unicode()
    armor_class = SL.Unicode()
    base_attack = SL.Unicode()
    grapple = SL.Unicode()
    attack = SL.Unicode()
    full_attack = SL.Unicode()
    space = SL.Unicode()
    reach = SL.Unicode()
    special_attacks = SL.Unicode()
    special_qualities = SL.Unicode()
    saves = SL.Unicode()
    abilities = SL.Unicode()
    skills = SL.Unicode()
    bonus_feats = SL.Unicode()
    feats = SL.Unicode()
    epic_feats = SL.Unicode()
    environment = SL.Unicode()
    organization = SL.Unicode()
    challenge_rating = SL.Unicode()
    treasure = SL.Unicode()
    alignment = SL.Unicode()
    advancement = SL.Unicode()
    level_adjustment = SL.Unicode()
    special_abilities = SL.Unicode()
    stat_block = SL.Unicode()
    full_text = SL.Unicode()
    reference = SL.Unicode()
    image = SL.Unicode()

    def __repr__(self):
        return '<%s name=%s>' % (self.__class__.__name__, self.name)

monsterCollection = StormFactCollection(Monster, 'monster')

class Spell(object):
    """A spell"""
    implements(IStormFact)

    __storm_table__ = 'spell'

    collection = None

    id = SL.Int(primary=True)                #
    name = SL.Unicode()
    full_text = SL.Unicode()
    altname = SL.Unicode()
    school = SL.Unicode()
    subschool = SL.Unicode()
    level = SL.Unicode()
    components = SL.Unicode()
    casting_time = SL.Unicode()
    range = SL.Unicode()
    target = SL.Unicode()
    area = SL.Unicode()
    duration = SL.Unicode()
    saving_throw = SL.Unicode()
    short_description = SL.Unicode()
    reference = SL.Unicode()

spellCollection = StormFactCollection(Spell, 'spell')


def joinRuleCamel(s):
    """
    join words in s in camelCase
    """
    s = re.sub(r'[^a-zA-Z0-9]', '', s)
    return s[0].lower() + s[1:]


def srdReferenceURL(item):
    """
    Return the URL at d20srd.org that describes the thing being looked up
    """
    mapper = {
'SRD 3.5 DivineDomainsandSpells': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 EpicMonsters(A-E)': ('http://www.d20srd.org/srd/epic/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 EpicMonsters(G-W)': ('http://www.d20srd.org/srd/epic/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 EpicSpells': ('http://www.d20srd.org/srd/epic/spells/%s.htm', joinRuleCamel),
'SRD 3.5 PsionicSpells': ('http://www.d20srd.org/srd/psionic/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsA-B': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsC': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsD-E': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsF-G': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsH-L': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsM-O': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsP-R': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsS': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 SpellsT-Z': ('http://www.d20srd.org/srd/spells/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersAnimals': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersB-C': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersD-De': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersDi-Do': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersDr-Dw': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersE-F': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersG': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersH-I': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersIntro-A': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersK-L': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersM-N': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersO-R': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersS': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersT-Z': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 MonstersVermin': ('http://www.d20srd.org/srd/monsters/%s.htm', joinRuleCamel),
'SRD 3.5 PsionicMonsters': ('http://www.d20srd.org/srd/psionic/monsters/%s.htm', joinRuleCamel),
}
    base, rule = mapper[item.reference]
    return base % (rule(item.name),)



## RDF-based facts
## RDF-based facts
## RDF-based facts

class IRDFFact(IRuleFact):
    """
    The SRD/RDF facts typically all have these special attributes, useful for
    various reasons.
    """
    label = Attribute("label")

    def collectText():
        """
        Collect all of the human-viewable text.
        """


class IndexableRDFFact(object):
    """
    Trivial layer over facts that are objects in the SRD/RDF, all of which
    have the necessary properties.
    """
    implements(IIndexable)
    __used_for__ = IRDFFact

    def __init__(self, fact):
        self.fact = fact
        self.text = fact.collectText()
        self.uri = unicode(fact.resUri)
        self.title = unicode(fact.label)

# Use IndexableStormFact as an adapter for stormfacts to convert them to
# IIndexable
globalRegistry.register([IRDFFact], IIndexable, '', IndexableRDFFact)


class RDFFactCollection(object):
    """
    A collection of RuleFacts that are RDFalchemy-mapped objects, so we can
    look them up or dump them.
    """
    implements(IRuleCollection, IPlugin)
    system = D20SRD35System
    def __init__(self, factClass, factName):
        factClass.collection = self
        self.klass = factClass
        self.factName = factName

    def __getitem__(self, key):
        ret = self.lookup(key)
        if not ret:
            raise KeyError(key)
        return ret

    def dump(self):
        """
        All instances of the factClass
        """
        return list(self.klass.ClassInstances())

    def lookup(self, uri):
        """
        Lookup an item by its uri.

        @return an instance of the table-mapped class, e.g. Monster, Spell,
        Feat or Skill
        """
        r = self.klass(u'<%s>' % (uri,))
        return r


class SpecialArmorClass(S.rdfsPTClass):
    """Permanent, racial modifier to armor class"""
    rdf_type = CHAR.SpecialArmorClass
    implements(IRDFFact)

    collection = None

    def collectText(self):
        """
        The indexable text of this special AC
        """
        t = unicode(self.comment)
        return t or unicode(self.label)

specialAC = RDFFactCollection(SpecialArmorClass, 'specialAC')


class Aura(S.rdfsPTClass):
    """
    Permanent effect that extends some distance around the body of the
    creature.
    """
    rdf_type = CHAR.Aura
    implements(IRDFFact)

    collection = None

    def collectText(self):
        """
        The indexable text of this aura
        """
        t = unicode(self.comment)
        return t or unicode(self.label)

aura = RDFFactCollection(Aura, 'aura')


class SpecialAction(S.rdfsPTClass):
    """Something a creature can do besides attack"""
    rdf_type = CHAR.SpecialAction
    implements(IRDFFact)

    collection = None

    def collectText(self):
        """
        The indexable text of this special action
        """
        t = unicode(self.comment)
        return t or unicode(self.label)

specialAction = RDFFactCollection(SpecialAction, 'specialAction')


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
    implements(IRDFFact)

    collection = None

    comment = rdfSingle(RDFSNS.comment)
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

    def collectText(self):
        """
        The indexable text of this family
        """
        t = unicode(self.comment)
        return textFromHtml(t or u'<p>NO_TEXT_HERE</p>')

family = RDFFactCollection(Family, 'family')


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
    implements(IRDFFact)

    collection = None

    keyAbility = rdfSingle(PROP.keyAbility, range_type=CHAR.AbilityScore)
    synergy = rdfMultiple(PROP.synergy, range_type=CHAR.SkillSynergy)
    additional = rdfSingle(PROP.additional)
    epicUse = rdfSingle(PROP.epicUse)
    skillAction = rdfSingle(PROP.skillAction)
    skillCheck = rdfSingle(PROP.skillCheck)
    tryAgainComment = rdfSingle(PROP.tryAgainComment)
    untrained = rdfSingle(PROP.untrained)
    comment = rdfSingle(RDFSNS.comment)
    reference = rdfSingle(PROP.reference)

    def collectText(self):
        """
        The indexable text of this skill
        """
        addl = self.additional or u''
        epic = self.epicUse or u''
        act = self.skillAction or u''
        chk = self.skillCheck or u''
        cm = self.comment or u''
        again = self.tryAgainComment or u''
        un = self.untrained or u''
        return u' '.join([cm, act, chk, un, again, epic, addl])

skill = RDFFactCollection(Skill, 'skill')


NO_CACHE = object()


class CachingDescriptor(object):
    """
    Read-only descriptor which can compute its return value and caches it on
    the instance, once computed
    """
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        attrName = "_CachingDescriptor_" + str(self.name)
        if instance is None:
            raise NotImplemented("this is an instance attribute, not meant to be used on the class")
        cached = getattr(instance, attrName, NO_CACHE)
        if cached is not NO_CACHE:
            return cached
        r = self.get(instance, owner)
        setattr(instance, attrName, r)
        return r


class BonusFeatFilter(CachingDescriptor):
    """
    Descriptor to get those feats which are bonus feats.
    """
    def get(self, instance, owner):
        ret = []
        for feat in instance.feats:
            if feat.isBonusFeat:
                ret.append(feat)
        return ret


class CoreFeatFilter(CachingDescriptor):
    """
    Descriptor to get feats filtered along various axes.  These all work by
    inspecting the value of a monster's feat.

    Pass in a matcher function, and only feats for which matcher returns true
    on value will be returned.
    """
    def __init__(self, name, matcher):
        self.matcher = matcher
        CachingDescriptor.__init__(self, name)

    def get(self, instance, owner):
        return [f for f in instance.feats if self.matcher(f.value)]


class Feat(S.rdfsPTClass):
    """A feat usable by monsters, such as Weapon Focus"""
    rdf_type = CHAR.Feat
    implements(IRDFFact)

    collection = None

    stackable              = S.rdfIsInstance(CHAR.StackableFeat)
    canTakeMultiple        = S.rdfIsInstance(CHAR.CanTakeMultipleFeat)
    epic                   = S.rdfIsInstance(CHAR.EpicFeat)
    psionic                = S.rdfIsInstance(CHAR.PsionicFeat)
    isArmorClassFeat       = S.rdfIsInstance(CHAR.ArmorClassFeat)
    isAttackOptionFeat     = S.rdfIsInstance(CHAR.AttackOptionFeat)
    isSpecialActionFeat    = S.rdfIsInstance(CHAR.SpecialActionFeat)
    isRangedAttackFeat     = S.rdfIsInstance(CHAR.RangedAttackFeat)
    isSpeedFeat            = S.rdfIsInstance(CHAR.SpeedFeat)
    
    additional             = rdfSingle(PROP.additional)
    benefit                = rdfSingle(PROP.benefit)
    choiceText             = rdfSingle(PROP.choiceText)
    prerequisiteText       = rdfSingle(PROP.prerequisiteText)
    noFeatComment          = rdfSingle(PROP.noFeatComment)
    comment                = rdfSingle(RDFSNS.comment)
    reference              = rdfSingle(PROP.reference)

    def collectText(self):
        """
        The indexable text of this skill
        """
        cm = self.comment or u''
        ben = self.benefit or u''
        prereq = self.prerequisiteText or u''
        choice = self.choiceText or u''
        addl = self.additional or u''
        nofeat = self.noFeatComment or u''
        return u' '.join([cm, ben, prereq, choice, nofeat, addl])

feat = RDFFactCollection(Feat, 'feat')


class Alignment(S.rdfsPTClass):
    """
    One of the 10 alignments (including none)
    """
    rdf_type               = CHAR.AlignmentTrue
    value                  = rdfSingle(RDF.value)


class AnnotatedValue(S.rdfsPTClass):
    """
    A simple integer score, which may have annotations
    """
    value                  = rdfSingle(RDF.value)


class MonsterFeat(S.rdfsPTClass):
    """
    A feat possessed by a particular monster, which may be a bonus feat
    """
    rdf_type = CHAR.MonsterHasFeat
    value                  = rdfSingle(RDF.value, range_type=Feat.rdf_type)
    isBonusFeat            = S.rdfIsInstance(CHAR.MonsterBonusFeat)
    timesTaken             = rdfSingle(PROP.featTimesTaken)


class Monster2(S.rdfsPTClass):
    """
    A creature statted from the SRD monster list

    Explicitly excluded: armor_class (is armorClass), full_attack (is
    attackGroups list), special_qualities (is fullAbilities or something else
    if we rename that), special_abilities (is multiple of specialAbility),
    stat_block (dropped, redundant), full_text (is fullText)

    """
    rdf_type = CHAR.Monster

    family                 = rdfSingle(PROP.family)             # DONE!
    altname                = rdfSingle(PROP.altname)            # DONE!
    size                   = rdfSingle(PROP.size)               # DONE!
    type                   = rdfSingle(PROP.type)               # DONE!
    _descriptors           = rdfMultiple(PROP.descriptor)       # DONE!
    hitDice                = rdfSingle(PROP.hitDice)            # DONE!
    # hitPoints will always be computed by outside app.
    # count will always be outside app
    # label will always be outside app

    environment            = rdfSingle(PROP.environment)        # DONE!
    organization           = rdfSingle(PROP.organization)       # DONE!
    cr                     = rdfMultiple(PROP.cr)               # DONE!

    _alignments            = rdfMultiple(PROP.alignment,
                                range_type=CHAR.AlignmentTrue)  # DONE!

    advancement            = rdfSingle(PROP.advancement)        # DONE!
    levelAdjustment        = rdfSingle(PROP.levelAdjustment)    # DONE!

    image                  = rdfSingle(PROP.image)              # DONE!

    initiative             = rdfSingle(PROP.initiative)         # DONE!
    speed                  = rdfSingle(PROP.speed)              # DONE!
    bab                    = rdfSingle(PROP.bab)                # DONE!
    grapple                = rdfSingle(PROP.grapple)            # DONE!

    space                  = rdfSingle(PROP.space)              # DONE!
    reach                  = rdfSingle(PROP.reach)              # DONE!

    _saves                 = rdfMultiple(PROP.save)             # DONE!  

    _abilities             = rdfMultiple(PROP.abilityScore)     # DONE!  

    _treasures             = rdfMultiple(PROP.treasure)         # DONE!
    treasureNotes          = rdfSingle(PROP.treasureNotes)      # DONE!

    TODO("""_saves and _treasures and _abilities are lists, so we must
    reconstruct the whole list to set any of them, and we must iterate the
    whole list to get any of them.  Implement an associative type""")

    feats                  = rdfMultiple(PROP.feat, range_type=CHAR.MonsterHasFeat)
    bonusFeats             = BonusFeatFilter("bonusFeats")
    acFeats                = CoreFeatFilter("acFeats", 
                                            lambda x: x.isArmorClassFeat)
    speedFeats             = CoreFeatFilter("speedFeats", 
                                            lambda x: x.isSpeedFeat)
    attackOptionFeats      = CoreFeatFilter("attackOptionFeats", 
                                            lambda x: x.isAttackOptionFeat)
    rangedAttackFeats      = CoreFeatFilter("rangedAttackFeats", 
                                            lambda x: x.isRangedAttackFeat)
    epicFeats              = CoreFeatFilter("epicFeats", 
                                            lambda x: x.epic)


    TODO("""listen and spot will be property()'s of Monster2.  Values will be
    computed by examining self.skills
    """)
#"     listen
#"     spot

#"     armorClass             = rdfSingle(...)  # write a parser

#"     attackGroups           = rdfSingle(...)  # from sb.get - list

    TODO("""attack will be a property() of Monster2. value will be computed by
    returning attackGroups[0]
    """)
#"     attack

#"     languages              = rdfSingle(PROP.)                   # from sb.get? - list

#"     specialAttacks         = rdfList(...)  # from sb.get
#"     fullAbility            = rdfMultiple(...)  # from sb.get - maybe rename
#"     specialAbility         = rdfMultiple(PROP.specialAbility)           # list parsed from sb.get

    TODO("""specialAC, 
    spellLikeAbilities, 
    casterLevel, 
    spellResistance, 
    aura,
    fastHealing, 
    regeneration, 
    damageReduction, 
    immunities, 
    senses,
    resistances, 
    vulnerabilities 
    ... will be computed by looking at self.fullAbilities and
    self.specialAttacks and self.specialAbility""")

    TODO("""damageReduction, 
    senses, 
    immunities, 
    resistances,
    vulnerabilities 
    are dictionaries, though.""")

#"     skills                 = rdfMultiple(PROP.skill, ...)  # dict from sb.parseSkills

    TODO("""fullText should be a link into an HTML document which contains all
    of the full texts, with the parts that are already covered by the data
    removed.  We need an automatic way to determine which part of the HTML
    documents to keep, and an automatic way to determine which monsters should
    share which fulltexts.""")
#"    fullText               = rdfSingle(...)  # clean up from sql
#"    reference              = rdfSingle(...)  # from d20srd35.srdReferenceURL

TODO("""monster2 = RDFFactCollection(Monster2, 'monster2')""")

TODO("""Extremely important TODO: add author/license/creation date/etc.
metadata to everything here, so publishers can describe their work using
friggin' RDF.""")

mapper()

