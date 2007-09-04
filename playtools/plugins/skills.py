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

from twisted.python.util import sibpath

class Skill(object):
    __storm_table__ = 'skill'
    id = SL.Int(primary=True)                #
    name = SL.Unicode()                      #
    subtype = SL.Unicode()
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


SKILL_TEMPLATE = string.Template(''':$rdfName
    rdfs:label "${label}";
    p:keyAbility ${keyAbility};
    p:skillAction "${action}";
${retryable}${psionic}${trained}${armorCheck}
    p:reference <http://www.d20srd.org/srd/${reference}>;
    p:additional "${special}";
    p:restriction "${restriction}";
    p:untrained "${untrained}";
.
''')

RETRYABLE = "    a c:RetryableSkill;"
PSIONIC = "    a c:PsionicSkill;"
TRAINED = "    a c:RequiresRanks;"
ARMORCHECK = "    a c:ArmorCheckPenalty;"


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

    def __iter__(self):
        return self

    def next(self):
        return self.skillSource.next()

    def writePlaytoolsItem(self, playtoolsIO, c):
        r = rdfName(c.name)
        origR = r
        
        # for skills with same name, increment a counter on the rdfName
        if r in self._seenNames:
            self._seenNames[r] = self._seenNames[r] + 1
            r = "%s%s" % (r, self._seenNames[r])
        else:
            self._seenNames[r] = 1

        retryable = (RETRYABLE if srdBoolean(c.try_again) else '')
        psionic = (PSIONIC if srdBoolean(c.psionic) else '')
        trained = (TRAINED if srdBoolean(c.trained) else '')
        armorCheck = (ARMORCHECK if srdBoolean(c.armor_check) else '')

        if psionic:
            reference = "psionic/skills/%s.htm" % (origR,)
        else:
            reference = "skills/%s.htm" % (origR,)

        s = SKILL_TEMPLATE.substitute(
            dict(rdfName=r,
                label=c.name,
                action=c.action or '',
                special=c.special or '',
                restriction=c.restriction or '',
                keyAbility="c:%s" % (c.key_ability.lower(),),
                retryable=retryable,
                psionic=psionic,
                trained=trained,
                untrained=c.untrained or '',
                reference=reference,
                armorCheck=armorCheck,
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

        playtoolsIO.writeXml('\n')
        playtoolsIO.writeXml(desc)
        playtoolsIO.writeXml('\n')
        playtoolsIO.writeXml(skillCheck)
        playtoolsIO.writeXml('\n')
        playtoolsIO.writeXml(epicUse)
        playtoolsIO.writeXml('\n')
        playtoolsIO.writeXml(fullText)

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


ss = skillSource(sibpath(__file__, 'srd35.db'))
skillConverter = SkillConverter(ss)
