"""
Query the sqlite database of monsters for matching monsters.
"""
import string
import re

from zope.interface import implements

from storm import locals as SL

from .util import RESOURCE
from .interfaces import IRuleFact

class Monster(object):
    """A Monster mapped from the db"""
    implements(IRuleFact)

    __storm_table__ = 'monster'

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


class Spell(object):
    """A spell"""
    implements(IRuleFact)

    __storm_table__ = 'spell'

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


class SRDDatabase(object):
    """A complete SRD database"""
    def __init__(self):
        self.db = SL.create_database('sqlite:///' + RESOURCE('srd35.db'))
        self.store = SL.Store(self.db)

    def lookup(self, idOrName, klass):
        """
        Implement the dual-interpretation logic for "idOrName" to look
        up an object from the database by id or by name.  Naturally
        this requires the table have a 'name' column.
        
        @return an instance of the table-mapped class, e.g. Monster, Spell,
        Feat or Skill
        """
        try:
            id = int(idOrName)
            thing = self.store.find(klass, klass.id==id).one()
            if thing is not None:
                return thing
        except ValueError:
            pass
        return self.store.find(klass, klass.name==idOrName).one()

    def _allSkillStats(self):
        """Return all skill names as strings"""
        return [m.skills for m in self.store.find(Monster)]

    def _allHPStats(self):
        """Return all hit dice as strings"""
        return [m.hit_dice for m in self.store.find(Monster)]

    def _allFeatStats(self):
        """Return all feat names as strings"""
        return [m.feats for m in self.store.find(Monster)]

    def _allAttackStats(self):
        """Return all attacks for all monsters"""
        return [(m.id, m.full_attack) for m in self.store.find(Monster)]

    def _allFullTextStats(self):
        """Return all attacks for all monsters"""
        return [(m.id, m.full_text) for m in self.store.find(Monster)]

    def _allSQStats(self):
        """Return all special qualitier for all monsters"""
        return [(m.id, m.special_qualities) for m in self.store.find(Monster)]

    def _allSaveStats(self):
        """Return all save names as strings"""
        return [m.saves for m in self.store.find(Monster)]

    def allSpells(self):
        return list(self.store.find(Spell))

    def allMonsters(self):
        return list(self.store.find(Monster))

    def _allIds(self):
        return [m.id for m in self.store.find(Monster)]

db = SRDDatabase()

def lookup(id, klass=Monster):
    """
    Return the Monster for this id
    """
    return db.lookup(id, klass=klass)

def _allSkillStats():
    """Return the skill attribute for every monster"""
    return db._allSkillStats()

def _allFeatStats():
    """Return the feat attribute for every monster"""
    return db._allFeatStats()

def _allSaveStats():
    """Return the save attribute for every monster"""
    return db._allSaveStats()

def _allAttackStats():
    """Return the full_attack attribute for every monster"""
    return db._allAttackStats()

def _allFullTextStats():
    """Return the full_attack attribute for every monster"""
    return db._allFullTextStats()

def _allSQStats():
    """Return the special_qualities attribute for every monster"""
    return db._allSQStats()

def allMonsters():
    return db.allMonsters()

def _allIds():
    return db._allIds()

def _allHPStats():
    return db._allHPStats()

def allSpells():
    return db.allSpells()
