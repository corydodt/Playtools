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
from playtools.parser import abilityparser, saveparser

from playtools.plugins import d20srd35


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

# TODO - unit tests for these little parsers
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

    global badTreasures
    badTreasures = badTreasures + 1
    print 'bad treasure', s, badTreasures
    return s


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
    badCr = badCr + 1
    print 'bad cr', s, badCr
    return s


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
        return s
    if l:
        return l
    return C.noAlignment


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
        m = d20srd35.Monster2()

        def set(what, toWhat):
            """
            Set the new monster's what only if toWhat is a real thing
            """
            if toWhat:
                setattr(m, what, toWhat)

        # all of these are direct from the sql
        orig = sb.monster

        set('label',             orig.name)
        set('altname',           orig.altname)

        # TODO - use nodes for family/type/descriptor when known, otherwise
        # fallback to string - use statblock.Statblock.determineFamilies()
        set('family',            orig.family)
        set('type',              orig.type)
        set('descriptor',        orig.descriptor)

        # TODO - parser for size
        set('size',              orig.size)
        set('initiative',        parseInitiative(orig.initiative))
        set('speed',             orig.speed)
        # TODO - parse bab
        set('bab',               orig.base_attack)
        # TODO - I would like a grapple parser
        set('grapple',           orig.grapple)
        # TODO - space and reach are of type ^^distance
        set('space',             orig.space)
        set('reach',             orig.reach)
        set('environment',       orig.environment)
        # TODO - ideally i should have a parser written for organization
        set('organization',      orig.organization)
        set('cr',                parseChallengeRating(orig.challenge_rating))
        set('treasure',          parseTreasure(orig.treasure))
        set('advancement',       orig.advancement)
        set('levelAdjustment',   orig.level_adjustment)
        set('alignment',         parseAlignment(sb.get('alignment')))

        # TODO - create an image resource
        set('image',             orig.image)

        # TODO - the problem with sb.get is that it always returns a string.
        # we don't even want to set properties unless there is some data
        # there.  Check for strings like "None" or "False" returned

        # TODO - hitdice is of type parseable dice expression
        set('hitDice',            sb.get('hitDice'))

        saves = saveparser.parseSaves(orig.saves)[0]

        FIXME("""construct a Save class in d20srd35 based on rdfsPTClass and
        give it a bonus, qualifier and splat attribute.  construct three of
        those things here, instancing c:Fort, c:Ref and c:Will.""")
        fort, ref, will = zip(*sorted(saves.items()))[1]
        set('saveFort',           fort.bonus)
        set('saveFortNote',       fort.qualifier or fort.splat)
        set('saveRef',            ref.bonus)
        set('saveRefNote',        ref.qualifier or ref.splat)
        set('saveWill',           will.bonus)
        set('saveWillNote',       will.qualifier or will.splat)

        FIXME("""construct an AbilityScore class in d20srd35 based on
        rdfsPTClass and give it a bonus, qualifier and splat attribute.
        construct six of those things here, instancing c:Str, c:Dex and
        so on.""")
        abilities = abilityparser.parseAbilities(orig.abilities)[0]
        cha, con, dex, int, str, wis = zip(*sorted(abilities.items()))[1]
        set('abilityStr',         str.bonus)
        set('abilityStrNote',     str.qualifier or str.splat)
        set('abilityDex',         dex.bonus)
        set('abilityDexNote',     dex.qualifier or dex.splat)
        set('abilityCon',         con.bonus)
        set('abilityConNote',     con.qualifier or con.splat)
        set('abilityInt',         int.bonus)
        set('abilityIntNote',     int.qualifier or int.splat)
        set('abilityWis',         wis.bonus)
        set('abilityWisNote',     wis.qualifier or wis.splat)
        set('abilityCha',         cha.bonus)
        set('abilityChaNote',     cha.qualifier or cha.splat)

        # TODO - boolean flags (for example type membership: ":foo a c:Monster")
        # require us to step out of sqlalchemy


    def label(self):
        return u"monsters"

    def preamble(self):
        openFile = open(RESOURCE('plugins/monsters_preamble.n3'))
        sparqly.extendGraphFromFile(self.graph, openFile)

    def writeAll(self, playtoolsIO):
        self.graph.serialize(destination=playtoolsIO, format='n3')


ss = statblockSource()
monsterConverter = MonsterConverter(ss)
