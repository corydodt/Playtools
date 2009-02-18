"""
Converter from srd35.db to monster.n3
"""
import re

from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.python import usage

from storm import locals as SL

from playtools.convert import IConverter
from playtools import sparqly
from playtools.common import monsterNs, P, C, a, RDFSNS
from playtools.util import RESOURCE, rdfName
from playtools.plugins.util import srdBoolean, initDatabase, cleanSrdXml

from twisted.python.util import sibpath


class Monster(object):
    __storm_table__ = 'monster'
    id = SL.Int(primary=True)                #
    name = SL.Unicode()                      #
    family = SL.Unicode()
    altname = SL.Unicode()                   #
    size = SL.Unicode()                      #
    type = SL.Unicode()
    descriptor = SL.Unicode()
    hit_dice = SL.Unicode()
    initiative = SL.Unicode()                #
    speed = SL.Unicode()                     #
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
    challenge_rating = SL.Unicode()          #
    treasure = SL.Unicode()                  #
    alignment = SL.Unicode()                 #
    advancement = SL.Unicode()
    level_adjustment = SL.Unicode()
    special_abilities = SL.Unicode()
    stat_block = SL.Unicode()
    full_text = SL.Unicode()
    reference = SL.Unicode()


def monsterSource(store):
    for p in store.find(Monster).order_by(Monster.name):
        yield p

def statblockSource(store):
    # blah, cross-dependencies :(
    from goonmill.history import Statblock

    for m in monsterSource(store):
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
        self.db.extendGraph(RESOURCE('plugins/monsters_preamble.n3'))

    def writeAll(self, playtoolsIO):
        playtoolsIO.write(self.db.dump())


store = initDatabase(sibpath(__file__, 'srd35.db'))
ss = statblockSource(store)
monsterConverter = MonsterConverter(ss)
