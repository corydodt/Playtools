"""
Parse special qualities, special attacks, all that shit.

There's an Australian fuck-ton (10% bigger than the English fuck-ton) of weird
shit that can happen in here, so basically split on commas and look for things
I understand, and whack anything else into an Unknown object.

"""
import operator
import re

from playtools.parser import diceparser
diceparser
from playtools.parser import attackparser
attackparser

from playtools.util import RESOURCE
from playtools.test.pttestutil import TODO

from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import chartypes, numbers
## appease pyflakes
chartypes, numbers


grammar = open(RESOURCE('parser/specialparser.txt')).read()

specialQualityParser = parser.Parser(grammar, root='specialQualityRoot')

simpleSpecialQualityParser = parser.Parser(grammar, 
        root='simpleSpecialRoot')


class Quality(object):
    count = 0
    miscs = {}

    def __init__(self, type, name=None):
        Quality.count = Quality.count + 1
        self.kw = {}
        self.type = type
        self.name = name
        if type == 'misc':
            name = name.lower()
            uq = Quality.miscs.get(name)
            if uq is None:
                self.miscs[name] = 1
            else:
                self.miscs[name] = uq + 1

    def setArgs(self, **kw):
        self.kw.update(kw)

    def __repr__(self):
        return "<Quality %s %s kw=%s>" % (self.type, self.name, self.kw.keys())

    def __getattr__(self, k):
        return self.kw.get(k)


spellLikes = { # {{{
'air walk': 1,
'animate objects': 1,
'antimagic field': 1,
'astral project': 1,
'astral projection': 1,
'bless': 1,
'blink': 1,
'blur': 1,
'charm person': 1,
'command plants': 1,
'command undead': 1,
'control water': 1,
'control weather': 1,
'control winds': 1,
'create/destroy water': 1,
'create food and water': 1,
'cure serious wounds': 1,
'darkness': 1,
'daylight': 1,
'detect good': 1,
'detect magic': 1,
'detect thoughts': 1,
'dimension door': 1,
'dire winter': 1,
'discern location': 1,
'displacement': 1,
'dominate person': 1,
'dominate monster': 1,
'endure elements': 1,
'energy drain': 1,
'entangle': 1,
'enthrall': 1,
'ethereal jaunt': 1,
'etherealness': 1,
'fear': 1,
'feather fall': 1,
'find the path': 1,
'fog cloud': 1,
'forcecage': 1,
'foresight': 1,
'freedom of movement': 1,
'gaseous form': 1,
'geas/quest': 1,
'greater invisibility': 1,
'gust of wind': 1,
'hallucinatory terrain': 1,
'haste': 1,
'hypnotic pattern': 1,
'imprisonment': 1,
'insect plague': 1,
'invisibility': 1,
'locate object': 1,
'magic circle against evil': 1,
'magic circle against good': 1,
'make whole': 1,
'maze': 1,
'mirage arcana': 1,
'move earth': 1,
'plane shift': 1,
'plant growth': 1,
'poison': 1,
'prismatic sphere': 1,
'prismatic wall': 1,
'rainbow pattern': 1,
'rage': 1,
'resilient sphere': 1,
'resistance': 1,
'reverse gravity': 1,
'scare': 1,
'sending': 1,
'shatter': 1,
'shield other': 1,
'slow': 1,
'speak with animals': 1,
'spider climb': 1,
'stone shape': 1,
'suggestion': 1,
'sunbeam': 1,
'sunburst': 1,
'telekinetic sphere': 1,
'teleport': 1,
'tongues': 1,
'trap the soul': 1,
'transmute rock to mud/mud to rock': 1,
'true seeing': 1,
'veil': 1,
'ventriloquism': 1,
'wall of force': 1,
'wall of ice': 1,
'wall of stone': 1,
'water breathing': 1,
'web': 1,
'whirlwind': 1,
} # }}}


class Processor(disp.DispatchProcessor):
    def specialQualityStat(self, (t,s1,s2,sub), buffer):
        self.specialQualities = []
        disp.dispatchList(self, sub, buffer)
        return self.specialQualities

    def difficultyClass(self, *a, **kw):
        return {'dc':int(disp.getString(*a, **kw))}

    def damagingQualityName(self, *a, **kw):
        return disp.getString(*a, **kw)

    def diceExpression(self, *a, **kw):
        return {'damage': disp.getString(*a, **kw).strip()}

    def exAttack(self, (t,s1,s2,sub), buffer):
        parts = disp.dispatchList(self, sub, buffer)
        if len(parts) > 0:
            q = Quality('damaging', parts.pop(0))
            for part in parts:
                q.setArgs(**part)
        self.specialQualities.append(q)

    def qualifier(self, *a, **kw):
        ql = disp.getString(*a, **kw)[1:-1]
        return {'qualifier':ql}

    def extraDamage1(self, *a, **kw):
        return {'extraDamage': disp.getString(*a, **kw).strip()}

    def rangedSenseName(self, *a, **kw):
        return disp.getString(*a, **kw)

    def rangedSense(self, (t,s1,s2,sub), buffer):
        ll = disp.dispatchList(self, sub, buffer)
        name = ll.pop(0)
        q = Quality('sense', name)
        self.specialQualities.append(q)
        for part in ll:
            q.setArgs(**part)

    def exMeleeAttack(self, (t,s1,s2,sub), buffer):
        q = Quality('exMeleeAttack', buffer[s1:s2])
        self.specialQualities.append(q)

    def noArgumentSense(self, (t,s1,s2,sub), buffer):
        q = Quality('sense', buffer[s1:s2])
        self.specialQualities.append(q)

    def noArgumentQuality(self, (t,s1,s2,sub), buffer):
        q = Quality(t, buffer[s1:s2])
        self.specialQualities.append(q)

    def auraArg(self, (t,s1,s2,sub), buffer):
        q = Quality('aura', 'Aura')
        q.setArgs(what=buffer[s1:s2].strip())
        self.specialQualities.append(q)

    def spells(self, (t,s1,s2,sub), buffer):
        q = Quality('spells', 'spells')
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)
        for part in ll:
            q.setArgs(**part)

    def spellsLevel(self, (t,s1,s2,sub), buffer):
        l = buffer[s1:s2]
        l = re.search(r'(\d+)', l).group(1)
        return {'level': int(l)}

    def vulnerabilityArg(self, (t,s1,s2,sub), buffer):
        q = Quality('vulnerability', 'Vulnerability')
        q.setArgs(what=buffer[s1:s2])
        self.specialQualities.append(q)

    def immunityArg(self, (t,s1,s2,sub), buffer):
        newQualities = []
        buf = buffer[s1:s2]
        if ' and ' in buf:
            imms = buf.split(' and ')
            for imm in imms:
                q = Quality('immunity', 'Immunity')
                q.setArgs(what=imm.strip())
                newQualities.append(q)
        else:
            q = Quality('immunity', 'Immunity')
            q.setArgs(what=buffer[s1:s2].strip())
            newQualities = [q]
        self.specialQualities.extend(newQualities)

    def resistanceName(self, (t,s1,s2,sub), buffer):
        q = Quality('resistance', 'Resistance')
        q.setArgs(what=buffer[s1:s2].strip())
        self.specialQualities.append(q)

    def resistanceAmount(self, (t, s1, s2, sub), buffer):
        self.specialQualities[-1].setArgs(amount=buffer[s1:s2])

    def regenerationArg(self, (t,s1,s2,sub), buffer):
        q = Quality('regeneration', 'Regeneration')
        q.setArgs(amount=buffer[s1:s2])
        self.specialQualities.append(q)

    def damageReductionArg(self, (t,s1,s2,sub), buffer):
        q = Quality('damageReduction', 'Damage Reduction')
        q.setArgs(amount=buffer[s1:s2])
        self.specialQualities.append(q)

    def fastHealingArg(self, (t,s1,s2,sub), buffer):
        q = Quality('fastHealing', 'Fast Healing')
        q.setArgs(amount=buffer[s1:s2])
        self.specialQualities.append(q)

    def empathyArg(self, (t,s1,s2,sub), buffer):
        q = Quality('empathy', 'Empathy')
        q.setArgs(what=buffer[s1:s2])
        self.specialQualities.append(q)

    def familyArg(self, (t,s1,s2,sub), buffer):
        q = Quality('family')
        q.setArgs(what=buffer[s1:s2])
        self.specialQualities.append(q)

    def empty(self, (t,s1,s2,sub), buffer):
        pass

    def miscName(self, *a,**kw):
        return disp.getString(*a, **kw).strip()

    TODO("spellLike abilities filtered for Su",
            """Spell-like abilities are spell-like UNLESS they are also
            encountered in the special_abilities block, and are tagged "Su" or
            "Ex" in that block.""")
    def miscQuality(self, (t,s1,s2,sub), buffer):
        ll = disp.dispatchList(self, sub, buffer)
        name = ll.pop(0)
        if name.lower() in spellLikes:
            q = Quality('spellLike')
            q.setArgs(spell=name)
            self.specialQualities.append(q)
        else:
            q = Quality('misc', name)
            self.specialQualities.append(q)
            for part in ll:
                q.setArgs(**part)

    def range(self, (t,s1,s2,sub), buffer):
        return {'range': buffer[s1:s2].strip()}

    def frightfulPresence(self, (t,s1,s2,sub), buffer):  
        q = Quality("aura", "Frightful presence")
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)
        for part in ll:
            q.setArgs(**part)

    def breathWeapon(self, (t,s1,s2,sub), buffer):
        q = Quality("damaging", "Breath weapon")
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)

        for part in ll:
            if part:
                q.setArgs(**part)

    def breathEffect(self, *a, **kw):
        return {'effect': disp.getString(*a, **kw).strip()}

    def breathPrismatic(self, *a, **kw):
        return {'effect': disp.getString(*a, **kw).strip()}

    def summon(self, (t,s1,s2,sub), buffer):
        q = Quality('summon', 'Summon')
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)
        for part in ll:
            q.setArgs(**part)

    def summonTarget(self, *a, **kw):
        return {'what': disp.getString(*a, **kw).strip()}

    def simpleSpecialStat(self, (t,s1,s2,sub), buffer):
        self.simples = []
        disp.dispatchList(self, sub, buffer)
        return self.simples

    def simpleName(self, *a, **kw):
        simp = SimpleQuality()
        self.simples.append(simp)
        simp.name = disp.getString(*a, **kw).strip()

    def useCategory(self, *a, **kw):
        s = disp.getString(*a, **kw).lower()
        self.simples[-1].useCategory = s

def parseSpecialQualities(s):
    """
    Return list of qualities
    """
    succ, children, end = specialQualityParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid special quality stat' % (s,))
    qualities = children[0]
    return qualities


class SimpleQuality(object):
    """
    A simpler representation as taken from orig_monster.special_abilities.
    Only name and useCategory are available
    """
    __slots__ = ['name', 'useCategory']


def parseSimpleSpecial(s):
    """
    Return list of qualities
    """
    if not s:
        return []

    succ, children, end = simpleSpecialQualityParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid simple special quality stat' % (s,))
    simples = children[0]
    return simples


def printFrequenciesOfUnknowns():
    items = Quality.miscs.items()
    for n, (k, freq) in enumerate(items):
        items[n] = freq, k

    print
    for q in sorted(items, key=operator.itemgetter(1)):
        print '{0: <5}{1}'.format(*q)
    print

    print sum(zip(*items)[0]), "total miscs"
    print Quality.count, "total qualities parsed"


