"""
Converter from srd35.db to feat.n3
"""
from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.python import usage

from storm import locals as SL

from playtools.convert import IConverter
from playtools import sparqly
from playtools.common import featNs, P, C, a, RDFSNS
from playtools.util import RESOURCE, rdfName
from playtools.plugins.util import srdBoolean, initDatabase

from twisted.python.util import sibpath


class Feat(object):
    __storm_table__ = 'feat'
    id = SL.Int(primary=True)                #
    name = SL.Unicode()                      #
    type = SL.Unicode()                      #
    multiple = SL.Unicode()                  #
    stack = SL.Unicode()                     #
    choice = SL.Unicode()
    prerequisite = SL.Unicode()
    benefit = SL.Unicode()                   #
    normal = SL.Unicode()                    #
    special = SL.Unicode()                   #
    full_text = SL.Unicode()                 #
    reference = SL.Unicode()                 #
    is_ac_feat = SL.Bool()                   #
    is_speed_feat = SL.Bool()                #
    is_attack_option_feat = SL.Bool()        #
    is_special_action_feat = SL.Bool()       #
    is_ranged_attack_feat = SL.Bool()        #


def featSource(store):
    for p in store.find(Feat).order_by(Feat.name):
        yield p


class Options(usage.Options):
    synopsis = "feats"


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


class FeatConverter(object):
    """Convert the Sqlite feat table

    To make it easier to test, the converter takes a featSource which is an
    generator of Feat items. 
    """
    implements(IConverter, IPlugin)
    commandLine = Options

    def __init__(self, featSource):
        self.featSource = featSource
        self._seenNames = {}
        pfx = { 'p': P, 'rdfs': RDFSNS, 'c': C, '': featNs }
        self.db = sparqly.TriplesDatabase(base=featNs, prefixes=pfx, datasets=[])

    def __iter__(self):
        return self

    def next(self):
        return self.featSource.next()

    def addTriple(self, s, v, *o):
        if s == None or v == None or None in o:
            return
        self.db.addTriple(featNs[s], v, *o)

    def makePlaytoolsItem(self, item):
        r = rdfName(item.name)
        origR = r

        ## # for feats with same name, increment a counter on the rdfName
        ## assert r not in self._seenNames
        ## if r in self._seenNames:
        ##     self._seenNames[r] = self._seenNames[r] + 1
        ##     r = "%s%s" % (r, self._seenNames[r])
        ## else:
        ##     self._seenNames[r] = 1

        def add(v, *o):
            self.addTriple(r, v, *o)

        add(RDFSNS.label, item.name)
        add(a, C.Feat)
        types = []
        for t in item.type.split(','):
            t = rdfName(t.strip()).capitalize() + "Feat"
            types.append(t)
        for type in types:
            add(a, getattr(C, type))
        if srdBoolean(item.multiple):
            add(a, C.CanTakeMultipleFeat)
        if srdBoolean(item.stack):
            add(a, C.StackableFeat)
        if item.choice:
            add(P.choiceText, item.choice)
        if item.prerequisite:
            add(P.prerequisiteText, item.prerequisite)
        if item.benefit:
            add(P.benefit, cleanSrdXml(item.benefit))
        if item.normal:
            add(P.noFeatComment, item.normal)

        if 'EpicFeat' in types:
            reference = "epic/feats.htm#%s" % (origR,)
        elif r in ['improvedFlybyAttack', 'improvedMultiattack', 
                'improvedMultiweaponFighting', 
                'greaterMultiweaponFighting']:
            reference = "epic/feats.htm#%s" % (origR,)
        elif 'PsionicFeat' in types:
            reference = "psionic/psionicFeats.htm#%s" % (origR,)
        else:
            reference = "feats/feats.htm#%s" % (origR,)
        add(P.reference, 
                sparqly.URIRef("http://www.d20srd.org/srd/%s" % (reference,)))

        if item.special:
            add(P.additional, item.special)

        if item.is_ac_feat:
            add(a, C.ArmorClassFeat)
        if item.is_speed_feat:
            add(a, C.SpeedFeat)
        if item.is_attack_option_feat:
            add(a, C.AttackOptionFeat)
        if item.is_special_action_feat:
            add(a, C.SpecialActionFeat)
        if item.is_ranged_attack_feat:
            add(a, C.RangedAttackFeat)

        ## - do we really care about fullText?
        ## if item.full_text:
        ##    add(P.fullText, cleanSrdXml(item.full_text))

    def label(self):
        return u"feats"

    def preamble(self):
        self.db.extendGraph(RESOURCE('plugins/feats_preamble.n3'))

    def writeAll(self, playtoolsIO):
        playtoolsIO.write(self.db.dump())


store = initDatabase(sibpath(__file__, 'srd35.db'))
ss = featSource(store)
featConverter = FeatConverter(ss)
