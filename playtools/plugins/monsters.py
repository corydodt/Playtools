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
from playtools.parser import abilityparser, saveparser

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

def parseTreasure(s):
    if s is None:
        return C.standardTreasure

    s = s.lower()
    if s == 'standard':
        return C.standardTreasure
    if s == 'double standard':
        return C.doubleStandardTreasure
    if s == 'triple standard':
        return C.tripleStandardTreasure
    if s == 'none':
        return C.noTreasure

    return s

"""bad treasures: {{{
      1/10th coins, 50% goods (no nonmetal or nonstone), 50% items (no nonmetal or nonstone) ** (1)
                                                     1/10th coins; 50% goods; standard items ** (1)
                                                             1/5 coins; 50% goods; 50% items ** (1)
                                                                      +2 chain shirt barding ** (1)
                                                                                as character ** (1)
                                                                    double goods (gems only) ** (1)
                                       double standard (nonflammables only) and +3 longspear ** (1)
             double standard plus +4 half-plate armor and gargantuan +3 adamantine warhammer ** (1)
                                                                               half standard ** (1)
                                                  no coins; 1/4 goods (honey only); no items ** (1)
                           no coins; 50% goods (metal or stone only); 50% items (no scrolls) ** (1)
                                                  no coins, 50% goods (stone only), no items ** (1)
                                                  no coins; 50% goods (stone only); no items ** (1)
                                                      no coins; standard goods; double items ** (1)
                                                               nonstandard (just its dagger) ** (1)
      standard coins; double goods (nonflammables only); standard items (nonflammables only) ** (1)
                                                standard coins, double goods, standard items ** (1)
                        standard coins; double goods; standard items, plus 1d4 magic weapons ** (1)
 standard coins; double goods; standard items, plus +1 vorpal greatsword and +1 flaming whip ** (1)
                                  standard coins; standard goods (gems only); standard items ** (1)
    standard coins; standard goods (nonflammables only); standard items (nonflammables only) ** (1)
                  standard (including +1 hide armor, +1 greatclub and ring of protection +1) ** (1)
                                                              standard (including equipment) ** (1)
                                                       standard plus possessions noted below ** (1)
                         standard, plus rope and +1 flaming composite longbow (+5 str bonus) ** (1)
                                                                         standard (see text) ** (1)
                                                     1/2 coins; double goods; standard items **** (2)
                                                             50% coins; 50% goods; 50% items **** (2)
                                                              no coins; 50% goods; 50% items **** (2)
                                                               standard (nonflammables only) **** (2)
                                                          1/10th coins; 50% goods; 50% items ******** (4)
                                                      no coins; double goods; standard items ****************** (9)
                                                standard coins; double goods; standard items ************************* (12)
                                                            1/10 coins; 50% goods; 50% items ************************************************** (24)
""" # }}}


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
        return 1./int(s[2:])
    else:
        try:
            return int(s)
        except ValueError:
            pass

    global badCr
    badCr = badCr +
    print >>sys.stderr, 'bad cr', s, badCr
    return s

"""bad cr: {{{
\"
1 (see text)
5 (noble 8)
8 (elder 9)
4 (normal);\n6 (pyro- or cryo-)
5 (normal);\n7 (pyro- or cryo-)
6 (normal);\n8 (pyro- or cryo-)
7 (normal);\n9 (pyro- or cryo-)
8 (normal);\n10 (pyro- or cryo-)
9 (normal);\n11 (pyro- or cryo-)
10 (normal);\n12 (pyro- or cryo-)
11 (normal);\n13 (pyro- or cryo-)
2 (without pipes) or 4 (with pipes)
4 (5 with irresistible dance)
Included with master
""" # }}}


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
        set('cr',                parseChallengeRating(orig.challenge_rating))
        set('treasure',          parseTreasure(orig.treasure))
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

        def _makeValues(dct):
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

                x.value = parsed.bonus
                if parsed.qualifier or parsed.splat:
                    x.comment = parsed.qualifier or parsed.splat
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

    def label(self):
        return u"monsters"

    def preamble(self):
        openFile = open(RESOURCE('plugins/monsters_preamble.n3'))
        sparqly.extendGraphFromFile(self.graph, openFile)

    def writeAll(self, playtoolsIO):
        self.graph.serialize(destination=playtoolsIO, format='n3')


ss = statblockSource()
monsterConverter = MonsterConverter(ss)
