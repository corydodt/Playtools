"""
Converter from srd35.db to monster.n3
"""
import sys

from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.python import usage

from rdflib import ConjunctiveGraph as Graph

from playtools.interfaces import IConverter
from playtools import sparqly
from playtools.common import monsterNs, P, C, a, RDFSNS
from playtools.util import RESOURCE, rdfName
from playtools.plugins.util import srdBoolean, initDatabase, cleanSrdXml
from playtools.parser import abilityparser, saveparser, treasureparser

from playtools.plugins import d20srd35
from playtools.test.util import TODO, FIXME


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

TODO("unit tests for these little parsers")

def parseInitiative(s):
    """
    Some initiatives include explanations (show the math).  We consider these
    excess verbiage, and drop them.
    """
    splits = s.split(None, 1)
    if len(splits) == 1:
        return int(s)
    return int(splits[0])


def parseChallengeRating(s):
    if s.startswith('1/'):
        return [((1./int(s[2:])), None,)]
    else:
        try:
            return [(int(s), None)]
        except ValueError:
            items = map(unicode.strip, s.split(';', 1))
            l = []
            for i in items:
                parts = i.split(None, 1)
                if len(parts)>1:
                    l.append((int(parts[0]), parts[1]))
                else:
                    l.append((int(parts[0]), None))
            return l


def parseSize(s):
    s = s.lower()
    if s == 'colossal+':
        return C.colossalPlus
    return getattr(C, s.lower())


def parseAlignment(s):
    l = []
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

    if l:
        return l
    return [C.noAlignment]

"""bad alignments: {{{
Any (same as creator)
As master
Lawful evil or chaotic evil
Neutral evil or neutral
Often lawful good\n(Deep: Usually lawful neutral or neutral)
Usually chaotic good\n(Wood: Usually neutral)
Usually chaotic neutral, neutral evil, or chaotic evil
Usually neutral good or neutral evil
""" # }}}

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
        self.graph = Graph()

    def __iter__(self):
        return self

    def next(self):
        return self.statblockSource.next()

    def makePlaytoolsItem(self, sb):
        sparqly.rdfsPTClass.db = self.graph
 
        orig = sb.monster

        m = d20srd35.Monster2(getattr(monsterNs, rdfName(orig.name)))

        def set(what, toWhat):
            """
            Set the new monster's what only if toWhat is a real thing
            """
            if toWhat:
                setattr(m, what, toWhat)

        set('label',             orig.name)
        set('altname',           orig.altname)

        TODO("""use nodes for family/type/descriptor when known, otherwise
        fallback to string - use statblock.Statblock.determineFamilies()""")
        set('family',            orig.family)
        set('type',              orig.type)
        set('descriptor',        orig.descriptor)

        set('size',              parseSize(orig.size))
        set('initiative',        parseInitiative(orig.initiative))
        set('speed',             orig.speed)
        TODO("parse bab")
        set('bab',               orig.base_attack)
        TODO("I would like a grapple parser")
        set('grapple',           orig.grapple)
        TODO("space and reach to be of type ^^distance")
        set('space',             orig.space)
        set('reach',             orig.reach)
        set('environment',       orig.environment)
        TODO("ideally I should have a parser written for organization")
        set('organization',      orig.organization)

        set('advancement',       orig.advancement)
        set('levelAdjustment',   orig.level_adjustment)
        set('alignment',         parseAlignment(sb.get('alignment')))

        TODO("create a dublin-core-style image resource")
        set('image',             orig.image)

        TODO("""the problem with sb.get is that it always returns a string.
        We don't even want to set properties unless there is some data there.
        Check for strings lke "None" or "False" returned.""")

        TODO("hitDice to be of type parseable dice expression")
        set('hitDice',            sb.get('hitDice'))

        defaultGetValue = lambda x: x.bonus
        defaultGetComment = lambda x: x.qualifier or x.bonus

        def _makeValues(dct, getValue=defaultGetValue, getComment=defaultGetComment):
            """
            Create an AnnotatedValue for each of the keys in dct
            """
            retlist = []
            for parsed, cls in dct.items():

                x = d20srd35.AnnotatedValue()

                # manually set the class
                self.graph.add((x.resUri, a, cls))
                # have to strip out "a rdfs:Class" for some reason added by rdfalc
                self.graph.remove((x.resUri, a, RDFSNS.Class))

                x.value = getValue(parsed)
                if getComment(parsed):
                    x.comment = getComment(parsed)
                retlist.append(x)

            return retlist

        # parse saves, then stack them up under _saves
        saves = saveparser.parseSaves(orig.saves)[0]
        fort, ref, will = zip(*sorted(saves.items()))[1]
        savelist = _makeValues({fort:C.Fort, ref:C.Ref, will:C.Will})
        set('_saves',             savelist)

        # parse abilities, then stack them up under _abilities
        abilities = abilityparser.parseAbilities(orig.abilities)[0]
        cha, con, dex, _int, _str, wis = zip(*sorted(abilities.items()))[1]
        ablist = _makeValues({cha:C.Cha, con:C.Con, dex:C.Dex, _int:C.Int,
                _str:C.Str, wis:C.Wis })
        set('_abilities',         ablist)

        # parse treasures, then stack them up under _treasures
        treasure, other = treasureparser.parseTreasures(orig.treasure)[0]
        coins, goods, items = zip(*sorted(treasure.items()))[1]
        getValueT = lambda x: x.value
        getCommentT = lambda x: x.qualifier
        tlist = _makeValues({coins:C.Coins, goods:C.Goods, items:C.Items},
                getValueT, getCommentT)
        set('_treasures',         tlist)
        if other:
            set('treasureNotes',  other)

        # challenge ratings are not differentiated by type (like saves and
        # abilities).  There are sometimes two different CR's, so make a list
        # like the others.
        crs = parseChallengeRating(orig.challenge_rating)
        d = {}
        for cr in crs: d[cr] = C.ChallengeRating
        crlist = _makeValues(d, lambda x:x[0], lambda x:x[1])
        set('cr',                 crlist)



    def label(self):
        return u"monsters"

    def preamble(self):
        openFile = open(RESOURCE('plugins/monsters_preamble.n3'))
        sparqly.extendGraphFromFile(self.graph, openFile)

    def writeAll(self, playtoolsIO):
        self.graph.serialize(destination=playtoolsIO, format='n3')


ss = statblockSource()
monsterConverter = MonsterConverter(ss)
