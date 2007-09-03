from zope.interface import implements
import string
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from twisted.plugin import IPlugin
from twisted.python import usage

from storm import locals as SL

from playtools.convert import IConverter, rdfName, rdfXmlWrap

from goonmill.util import RESOURCE as GR

class Skill(object):
    __storm_table__ = 'skill'
    id = SL.Int(primary=True)
    name = SL.Unicode()
    subtype = SL.Unicode()
    key_ability = SL.Unicode()
    psionic = SL.Unicode()
    trained = SL.Unicode()
    armor_check = SL.Unicode()
    description = SL.Unicode()
    skill_check = SL.Unicode()
    action = SL.Unicode()
    try_again = SL.Unicode()
    special = SL.Unicode()
    restriction = SL.Unicode()
    synergy = SL.Unicode()
    epic_use = SL.Unicode()
    untrained = SL.Unicode()
    full_text = SL.Unicode()
    reference = SL.Unicode()


def skillSource(dbPath):
    db = SL.create_database('sqlite:%s' % (dbPath,))
    store = SL.Store(db)
    for p in store.find(Skill).order_by(Skill.name):
        yield p


SKILL_TEMPLATE = string.Template(''':$rdfName
    rdfs:label "${label}";
    p:keyAbility ${keyAbility};
${retryable}${psionic}${trained}
    p:reference <http://www.d20srd.org/srd/skills/${rdfName}.htm>;
.
''')

RETRYABLE = "    a c:RetryableSkill;"
PSIONIC = "    a c:PsionicSkill;"
TRAINED = "    a c:RequiresRanks;"


class Options(usage.Options):
    synopsis = "SkillConverter"


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


class SkillConverter(object):
    """Convert the Sqlite skill table
    """
    implements(IConverter, IPlugin)
    commandLine = Options

    def __init__(self, skillSource):
        self.skillSource = skillSource
        self._seenNames = {}

    def __iter__(self):
        return self

    def next(self):
        return self.skillSource.next()

    def writePlaytoolsItem(self, playtoolsIO, c):
        r = rdfName(c.name)
        try:
            assert r not in self._seenNames
        except AssertionError:
            import sys, pdb; pdb.post_mortem(sys.exc_info()[2])
        self._seenNames[r] = 1
        if c.try_again is None:
            retryable = ''
        else:
            retryable = (RETRYABLE if c.try_again.lower() == "yes" else '')
        if c.psionic is None:
            psionic = ''
        else:
            psionic = (PSIONIC if c.psionic.lower() == "yes" else '')
        if c.trained is None:
            trained = ''
        else:
            trained = (TRAINED if c.trained.lower() == "yes" else '')

        s = SKILL_TEMPLATE.substitute(
            dict(rdfName=r,
                label=c.name,
                keyAbility="c:%s" % (c.key_ability.lower(),),
                retryable=retryable,
                psionic=psionic,
                trained=trained,
            )
        )

        playtoolsIO.writeN3(s)

        def wrap(s, p):
            if s is None:
                return u''
            return rdfXmlWrap(cleanSrdXml(s),
                about="http://thesoftworld.com/2007/skill.n3#%s" % (r,),
                predicate=(p, "http://thesoftworld.com/2007/property.n3#")
            )
        desc = wrap(c.description, "description")
        skillCheck = wrap(c.skill_check, "skillCheck")
        epicUse = wrap(c.epic_use, "epicUse")
        fullText = wrap(c.full_text, "fullText")

        playtoolsIO.writeXml(desc)

    def label(self):
        return u"SkillConverter"

    def n3Preamble(self, playtoolsIO):
        pre = """@prefix p: <http://thesoftworld.com/2007/property.n3#> .
@prefix c: <http://thesoftworld.com/2007/characteristic.n3#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<> rdfs:title "All d20 SRD Skills" .
"""
        playtoolsIO.writeN3(pre)


ss = skillSource(GR('srd35.db'))
skillConverter = SkillConverter(ss)
