"""
Converter from srd35.db to monster.n3
"""
import re
import sys

from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.python import usage

from rdflib import ConjunctiveGraph as Graph, URIRef

from playtools.interfaces import IConverter
from playtools import sparqly
from playtools.common import monsterNs, P, C, a, RDFSNS, skillNs
from playtools.util import RESOURCE, rdfName
from playtools.parser import (abilityparser, saveparser, treasureparser, 
        alignmentparser, skillparser)
from playtools.parser.misc import (parseInitiative, parseSize,
            parseChallengeRating, parseFamily, parseGrapple)

from playtools.plugins import d20srd35, monstertext
from playtools.test.pttestutil import TODO


def statblockSource():
    # fact loads plugins. we can't do that in this, a plugin, so this import
    # is hidden.
    from playtools import fact
    SRD = fact.systems['D20 SRD']

    # blah, cross-dependencies :(
    from goonmill.statblock import Statblock

    for m in SRD.facts['monster'].dump():
        yield Statblock.fromMonster(m)


class Options(usage.Options):
    synopsis = "monsters"


FAMRX = re.compile(r',\s*')

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

        refs = self.referenceURLs = {}
        for line in open(RESOURCE("plugins/monster/referencemap.txt")):
            name, ref, textloc = map(str.strip, line.split('\t'))
            refs[name] = [ref, textloc]

    def __iter__(self):
        return self

    def next(self):
        n = self.statblockSource.next()
        sys.stderr.write(n.get('name')[0])
        return n

    def makePlaytoolsItem(self, sb):
        # some rdf-based classes need to be told where their data store is.
        # We want the default to remain the sqlite-backed one used by SRD
        d20srd35.Monster2.db = self.graph
        d20srd35.MonsterFeat.db = self.graph
        d20srd35.AnnotatedValue.db = self.graph
        d20srd35.Alignment.db = self.graph
 
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

        set('family',            parseFamily(orig.family))
        set('type',              parseFamily(orig.type))
        _desc = []
        for item in FAMRX.split(orig.descriptor or ''):
            if item:
                _desc.append(parseFamily(item))
        if _desc:
            set('_descriptors',  _desc)

        set('size',              parseSize(orig.size))
        set('initiative',        parseInitiative(orig.initiative))
        set('speed',             orig.speed)
        if orig.base_attack is not None:
            set('bab',           int(orig.base_attack))
        set('grapple',           parseGrapple(orig.grapple))
        set('space',             orig.space)
        set('reach',             orig.reach)

        TODO("parser for environment")
        set('environment',       orig.environment)

        ## TODO("ideally I should have a parser written for organization")
        set('organization',      orig.organization)

        # alignment, with comment if any
        alignments = alignmentparser.parseAlignment(sb.get('alignment'))
        alnlist = []
        for _aln in alignments:
            al = d20srd35.Alignment()
            al.value = _aln[0]
            if len(_aln) > 1:
                al.comment = _aln[1]
            alnlist.append(al)
            # strip out "a AlignmentTrue" for some reason added by rdfalc
            self.graph.remove((al.resUri, a, C.AlignmentTrue))

        set('_alignments',       alnlist)

        set('advancement',       orig.advancement)
        set('levelAdjustment',   orig.level_adjustment)

        set('image',             orig.image)

        TODO("check that uses of sb.get are never using return as a bool",
        """the problem with sb.get is that it always returns a string.
        We don't even want to set properties unless there is some data there.
        Check for strings like "None" or "False" returned.""")

        set('hitDice',            sb.get('hitDice'))

        defaultGetValue = lambda x: x.bonus
        defaultGetComment = lambda x: x.qualifier

        def _makeValues(valueList, getValue=defaultGetValue, getComment=defaultGetComment):
            """
            Create an AnnotatedValue for each of the keys in dct
            """
            retlist = []
            for parsed, cls in valueList:

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
        savelist = _makeValues([(fort,C.Fort), (ref,C.Ref), (will,C.Will)])
        set('_saves',             savelist)

        # parse abilities, then stack them up under _abilities
        abilities = abilityparser.parseAbilities(orig.abilities)[0]
        cha, con, dex, _int, _str, wis = zip(*sorted(abilities.items()))[1]
        ablist = _makeValues(
                [(cha,C.Cha), (con,C.Con), (dex,C.Dex), (_int,C.Int),
                 (_str,C.Str), (wis,C.Wis)]
                )
        set('_abilities',         ablist)

        # parse treasures, then stack them up under _treasures
        treasure, other = treasureparser.parseTreasures(orig.treasure)[0]
        coins, goods, items = zip(*sorted(treasure.items()))[1]
        getValueT = lambda x: x.value
        getCommentT = lambda x: x.qualifier
        tlist = _makeValues(
                [(coins,C.Coins), (goods,C.Goods), (items,C.Items)],
                getValueT, getCommentT)
        set('_treasures',         tlist)
        if other:
            set('treasureNotes',  other)

        # challenge ratings are not differentiated by type (like saves and
        # abilities).  There are sometimes two different CR's, so make a list
        # like the others.
        crs = parseChallengeRating(orig.challenge_rating)
        d = []
        for cr in crs: d.append((cr, C.ChallengeRating))
        crlist = _makeValues(d, lambda x:x[0], lambda x:x[1])
        set('cr',                 crlist)

        # feats.  append extra data to each feat similar to AnnotatedValue,
        # but without the value (feats are either had or not had) and with a
        # couple of other attributes: times the feat was taken, and whether it
        # is a "bonus feat" (granted without prerequisites)
        _feats = sb.parseFeats()
        _myFeats = []
        for f in _feats:
            ff = d20srd35.MonsterFeat()
            if getattr(f, 'isBonusFeat', False):
                ff.isBonusFeat = True
            ff.value = f.dbFeat.resUri
            if f.qualifier is not None:
                ff.comment = f.qualifier
            if f.timesTaken:
                ff.timesTaken = f.timesTaken
            self.graph.remove((ff.resUri, a, C.MonsterHasFeat))
            _myFeats.append(ff)
        set('feats',               _myFeats)

        # reference and indexable text location
        res = m.resUri.partition('#')[-1]
        ref, textloc = self.referenceURLs[res]
        set('reference',           URIRef(ref))
        set('textLocation',        textloc)

        # skills, with notes
        if orig.skills:
            _sk = skillparser.parseSkills(orig.skills)[0]
        else:
            _sk = []
        _mySkills = []
        for sk in _sk:
            if not sk:
                continue
            res = rdfName(sk.skillName)
            # There are two nearly-identical concentrations. both are
            # denoted with "concentration" in the skill lists of monsters.
            # Apply :concentration2 if "psionic" monster
            if 'psionic' in m.reference and res == 'concentration':
                res = 'concentration2'
            _mySkills.append((sk, getattr(skillNs, res)))
        getValueSk = lambda x: x.value
        skillList = _makeValues(_mySkills, getValue=getValueSk)
        set('_skills',             skillList)

    def label(self):
        return u"monsters"

    def preamble(self):
        openFile = open(RESOURCE('plugins/monsters_preamble.n3'))
        sparqly.extendGraphFromFile(self.graph, openFile)

    def writeAll(self, playtoolsIO):
        self.graph.serialize(destination=playtoolsIO, format='n3')


ss = statblockSource()
monsterConverter = MonsterConverter(ss)
