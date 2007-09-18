try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.python import usage

from storm import locals as SL

from playtools.convert import IConverter, rdfName, rdfXmlWrap
from playtools.sparqly import TriplesDatabase, URIRef
from playtools.common import skillNs, P, C, a, RDFSNS, NS, this

from twisted.python.util import sibpath

class Skill(object):
    __storm_table__ = 'skill'
    id = SL.Int(primary=True)                #
    name = SL.Unicode()                      #
    subtype = SL.Unicode()                   #
    key_ability = SL.Unicode()               #
    psionic = SL.Unicode()                   #
    trained = SL.Unicode()                   #
    armor_check = SL.Unicode()               #
    description = SL.Unicode()               #
    skill_check = SL.Unicode()               #
    action = SL.Unicode()                    #
    try_again = SL.Unicode()                 #
    special = SL.Unicode()                   #
    restriction = SL.Unicode()               #
    synergy = SL.Unicode()
    epic_use = SL.Unicode()                  #
    untrained = SL.Unicode()                 #
    full_text = SL.Unicode()                 #
    reference = SL.Unicode()                 #


def skillSource(dbPath):
    db = SL.create_database('sqlite:%s' % (dbPath,))
    store = SL.Store(db)
    for p in store.find(Skill).order_by(Skill.name):
        yield p


class Options(usage.Options):
    synopsis = "skills"


def cleanSrdXml(s):
    """XML retrieved from the Sqlite SRD databases is
    - encoded in utf8, and
    - escaped on " and \
    this function decodes to unicode and un-escapes
    """
    u = s.decode('utf8')
    u = u.replace(r'\"', '"')
    u = u.replace(r'\n', '\n')
    u = u.replace(r'\\', '\\')
    return u


def srdBoolean(col):
    """
    True if the column is "yes"
    Otherwise False
    """
    if col is None:
        return False
    return col.lower().strip() == "yes"



class SkillConverter(object):
    """Convert the Sqlite skill table

    To make it easier to test, the converter takes a skillSource which is an
    generator of Skill items. 
    """
    implements(IConverter, IPlugin)
    commandLine = Options

    def __init__(self, skillSource):
        self.skillSource = skillSource
        self._seenNames = {}
        pfx = { 'p': P, 'rdfs': RDFSNS, 'c': C, '': skillNs }
        self.db = TriplesDatabase(base='http://thesoftworld.com/2007/skill.n3#', 
                prefixes=pfx, datasets=[])

    def __iter__(self):
        return self

    def next(self):
        return self.skillSource.next()

    def addTriple(self, s, v, *o):
        if s == None or v == None or None in o:
            return
        self.db.addTriple(skillNs[s], v, *o)

    def makePlaytoolsItem(self, item):
        r = rdfName(item.name)
        origR = r

        # for skills with same name, increment a counter on the rdfName
        if r in self._seenNames:
            self._seenNames[r] = self._seenNames[r] + 1
            r = "%s%s" % (r, self._seenNames[r])
        else:
            self._seenNames[r] = 1

        def add(v, *o):
            self.addTriple(r, v, *o)

        add(RDFSNS.label, item.name)
        add(P.keyAbility, item.key_ability.lower())
        if item.action:
            add(P.skillAction, item.action)
        if item.special:
            add(P.additional, cleanSrdXml(item.special))
        if item.restriction:
            add(P.restriction, item.restriction)
        if item.untrained:
            add(P.untrained, item.untrained)
        if srdBoolean(item.untrained):
            add(a, C.RetryableSkill)
        if srdBoolean(item.psionic):
            add(a, C.PsionicSkill)
            reference = "psionic/skills/%s.htm" % (origR,)
        else:
            reference = "skills/%s.htm" % (origR,)

        if srdBoolean(item.trained):
            add(a, C.RequiresRanks)
        if srdBoolean(item.armor_check):
            add(a, C.ArmorCheckPenalty)
        add(P.tryAgainComment, item.try_again)
        if item.description:
            add(RDFSNS.comment, cleanSrdXml(item.description))
        if item.skill_check:
            add(P.skillCheck, cleanSrdXml(item.skill_check))
        if item.epic_use:
            add(P.epicUse, cleanSrdXml(item.epic_use))
        # FIXME - do we really care about fullText?
        if item.full_text:
            add(P.fullText, cleanSrdXml(item.full_text))

        add(P.reference, 
                URIRef("http://www.d20srd.org/srd/%s" % (reference,)))

        subSkills = []
        if item.subtype:
            _subskillNames = item.subtype.split(',')
            for name in _subskillNames:
                rSubSkill = skillNs[rdfName(name)]
                subSkills.append(rSubSkill)
                self.db.addTriple(rSubSkill, a, C.SubSkill)
                self.db.addTriple(rSubSkill, RDFSNS.label, name)
            add(P['subSkills'], *subSkills)

    def label(self):
        return u"skills"

    def preamble(self):
        self.db.addTriple(this, RDFSNS['title'], "All d20 SRD Skills")

        # NOTE not!! self.addTriple
        add = lambda s,o,v: self.db.addTriple(skillNs[s], o, v)
        add('abyssal', a, C.Language)
        add('aquan', a, C.Language)
        add('auran', a, C.Language)
        add('celestial', a, C.Language)
        add('common', a, C.Language)
        add('draconic', a, C.Language)
        add('drowSignLanguage', a, C.Language)
        add('druidic', a, C.Language)
        add('dwarven', a, C.Language)
        add('elven', a, C.Language)
        add('formian', a, C.Language)
        add('giant', a, C.Language)
        add('gnoll', a, C.Language)
        add('gnome', a, C.Language)
        add('goblin', a, C.Language)
        add('grimlock', a, C.Language)
        add('halfling', a, C.Language)
        add('ignan', a, C.Language)
        add('infernal', a, C.Language)
        add('maenad', a, C.Language)
        add('orc', a, C.Language)
        add('sphinx', a, C.Language)
        add('sylvan', a, C.Language)
        add('terran', a, C.Language)
        add('undercommon', a, C.Language)
        add('worg', a, C.Language)
        add('xeph', a, C.Language)

    def writeAll(self, playtoolsIO):
        playtoolsIO.write(self.db.dump())


ss = skillSource(sibpath(__file__, 'srd35.db'))
skillConverter = SkillConverter(ss)
