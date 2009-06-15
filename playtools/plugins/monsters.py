"""
Converter from srd35.db to monster.n3
"""
from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.python import usage

from rdflib import ConjunctiveGraph as Graph

from playtools.interfaces import IConverter
from playtools import sparqly
from playtools.common import monsterNs, P, C, a, RDFSNS
from playtools.util import RESOURCE, rdfName
from playtools.plugins.util import srdBoolean, initDatabase, cleanSrdXml


def statblockSource():
    # fact loads plugins. we can't do that in this, a plugin, so this import
    # is hidden.
    from playtools import fact

    # blah, cross-dependencies :(
    from goonmill.statblock import Statblock

    SRD = fact.systems['D20 SRD']
    for m in SRD.facts['monster'].dump():
        yield Statblock.fromMonster(m)


class Options(usage.Options):
    synopsis = "monsters"

badTreasures = 0
badCr = 0
badAlignment = 0

def parseTreasure(s):
    if s is None:
        return (P.treasure, C.standardTreasure)

    s = s.lower()
    if s == 'standard':
        return (P.treasure, C.standardTreasure)
    if s == 'double standard':
        return (P.treasure, C.doubleStandardTreasure)
    if s == 'triple standard':
        return (P.treasure, C.tripleStandardTreasure)
    if s == 'none':
        return (P.treasure, C.noTreasure)

    global badTreasures
    badTreasures = badTreasures + 1
    print 'bad treasure', s, badTreasures
    return (P.treasureText, s)


def parseInitiative(s):
    """
    Some initiatives include explanations (show the math).  We consider these 
    excess verbiage, and drop them.
    """
    splits = s.split(None, 1)
    if len(splits) == 1:
        return (P.initiative, int(s))
    return (P.initiative, int(splits[0]))


def parseChallengeRating(s):
    if s.startswith('1/'):
        return (P.cr, 1./int(s[2:]))
    else:
        try:
            return (P.cr, int(s))
        except ValueError:
            pass

    global badCr
    badCr = badCr + 1
    print 'bad cr', s, badCr
    return (P.crText, s)


def parseAlignment(s):
    l = []
    bad = 0
    punct = '()'
    for word in s.split():
        word = word.lower().strip(punct)
        if word == 'none':
            l.append(C.noAlignment)
            continue
        if word in ['always', 'often', 'usually']:
            l.append(getattr(C, 'aligned%s' % (word.capitalize())))
            continue
        if word in ['neutral', 'lawful', 'chaotic', 'evil', 'good']:
            l.append(getattr(C, word))
            continue

        if word in ['any']:    # this word is stupid and devoid of meaning
            continue
        bad = 1

    if bad:
        global badAlignment
        badAlignment = badAlignment + 1
        print 'bad alignment', s, badAlignment
        return (P.alignmentText, s)
    if l:
        return [P.alignment] + l             
    return (P.alignment, C.noAlignment)


class MonsterConverter(object):
    """Convert the goonmill.history.History object to a rdf-based monster

    Other information is also loaded from the SQLite monster table
    """
    implements(IConverter, IPlugin)
    commandLine = Options

    def __init__(self, statblockSource):
        self.statblockSource = statblockSource
        self._seenNames = {}
        pfx = { 'p': P, 'rdfs': RDFSNS, 'c': C, '': monsterNs }
        self.db = sparqly.TriplesDatabase()
        self.db.open(None)

    def __iter__(self):
        return self

    def next(self):
        return self.statblockSource.next()

    def addTriple(self, s, v, *o):
        if s == None or v == None or None in o:
            return
        self.db.addTriple(monsterNs[s], v, *o)

    def makePlaytoolsItem(self, item):
        r = rdfName(item.get('name'))
        origR = r

        ## # for monsters with same name, increment a counter on the rdfName
        ## assert r not in self._seenNames
        ## if r in self._seenNames:
        ##     self._seenNames[r] = self._seenNames[r] + 1
        ##     r = "%s%s" % (r, self._seenNames[r])
        ## else:
        ##     self._seenNames[r] = 1

        def add(v, *o):
            self.addTriple(r, v, *o)

        add(RDFSNS.label, item.get('name'))
        add(a, C.Monster)
        add(*parseAlignment(item.get('alignment')))
        add(*parseTreasure(item.get('treasure')))
        add(*parseChallengeRating(item.get('challenge_rating')))
        add(P.size, rdfName(item.get('size')))
        add(*parseInitiative(item.get('initiative')))
        add(P.speedText, item.get('speed'))
        add(P.altName, item.get('altname'))

        print 'base_attack', item.get('base_attack')
        if item.get('base_attack') is None:
            import pdb; pdb.set_trace()

        ## if srdBoolean(item.stack):
        ##     add(a, C.StackableFeat)
        ## if item.normal:
        ##     add(P.noFeatComment, item.normal)
        ## if item.is_ranged_attack_feat:
        ##     add(a, C.RangedAttackFeat)

        ## - do we really care about fullText?
        ## if item.full_text:
        ##    add(P.fullText, cleanSrdXml(item.get("full_text")))

    def label(self):
        return u"monsters"

    def preamble(self):
        openFile = open(RESOURCE('plugins/monsters_preamble.n3'))
        self.db.extendGraphFromFile(openFile)

    def writeAll(self, playtoolsIO):
        playtoolsIO.write(self.db.dump())


ss = statblockSource()
monsterConverter = MonsterConverter(ss)
