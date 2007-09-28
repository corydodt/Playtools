"""
Converter from srd35.db to skill.n3 
"""
from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.python import usage

from storm import locals as SL

from playtools.convert import IConverter
from playtools.sparqly import TriplesDatabase, URIRef
from playtools.common import skillNs, P, C, a, RDFSNS
from playtools.util import RESOURCE, rdfName
from playtools.plugins.util import initDatabase, srdBoolean

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
    synergy = SL.Unicode()                   #
    epic_use = SL.Unicode()                  #
    untrained = SL.Unicode()                 #
    full_text = SL.Unicode()                 #
    reference = SL.Unicode()                 #


def skillSource(store):
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


def quoteSrdXml(s):
    """
    (almost) the opposite of cleanSrdXml, this escapes, with a \\, quotes newlines and quotes.
    This DOES NOT encode the string back to utf8.
    """
    s = s.replace('\\', r'\\')
    s = s.replace('\n', r'\n')
    s = s.replace('"', r'\"')
    return s


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
        self.db = TriplesDatabase(base=skillNs, prefixes=pfx, datasets=[])

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
        add(a, C.Skill)
        add(P.keyAbility, getattr(C, rdfName(item.key_ability.lower())))
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
        ## - do we really care about fullText?
        ## if item.full_text:
        ##    add(P.fullText, cleanSrdXml(item.full_text))

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
        self.db.extendGraph(RESOURCE('plugins/skills_preamble.n3'))

    def writeAll(self, playtoolsIO):
        playtoolsIO.write(self.db.dump())


store = initDatabase(sibpath(__file__, 'srd35.db'))
ss = skillSource(store)
skillConverter = SkillConverter(ss)
