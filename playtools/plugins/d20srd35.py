"""
The game system based on the D20 SRD (version 3.5)
"""
import re

from zope.interface import implements, Interface, Attribute

from twisted.plugin import IPlugin
from storm import locals as SL

from playtools.interfaces import (IRuleSystem, IRuleFact, IRuleCollection,
    IIndexable)
from playtools.util import RESOURCE
from playtools import globalRegistry
from playtools.search import textFromHtml


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


# the d20srd database is essentially static and permanent, so just open it here.
STORE = SL.Store(SL.create_database('sqlite:' + RESOURCE('plugins/srd35.db')))


class IStormFact(Interface):
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
    __used_for__ = IRuleFact

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
    systems = (D20SRD35System,)
    def __init__(self, factClass, factName):
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
    implements(IRuleFact, IPlugin, IStormFact)

    __storm_table__ = 'monster'
    factName = __storm_table__

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
    implements(IRuleFact, IPlugin, IStormFact)

    __storm_table__ = 'spell'
    factName = __storm_table__

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


