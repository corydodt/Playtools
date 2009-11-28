"""
Parse special_qualities, special_attacks, and special_abilities.  Ignores
perks from families; ignores perks from full_text.

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
from playtools.parser.ftabilityparser import Perk

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
            q = Perk(parts.pop(0), 'Ex', None)
            q.type = 'damaging' 
            for part in parts:
                for k,v in part.items():
                    setattr(q, k, v)
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
        q = Perk(name, None, None)
        q.type = 'sense'
        self.specialQualities.append(q)
        for part in ll:
            for k,v in part.items():
                setattr(q, k, v)

    def exMeleeAttack(self, (t,s1,s2,sub), buffer):
        q = Perk(buffer[s1:s2], 'Ex', None)
        q.type = 'exMeleeAttack'
        self.specialQualities.append(q)

    def noArgumentSense(self, (t,s1,s2,sub), buffer):
        q = Perk(buffer[s1:s2], None, None)
        q.type = 'sense'
        self.specialQualities.append(q)

    def noArgumentQuality(self, (t,s1,s2,sub), buffer):
        q = Perk(buffer[s1:s2], None, None)
        q.type = t
        self.specialQualities.append(q)

    def auraArg(self, (t,s1,s2,sub), buffer):
        q = Perk('Aura', None, None)
        q.type = 'aura'
        q.damageType = buffer[s1:s2].strip()
        self.specialQualities.append(q)

    otherAura = auraArg

    def specialAC(self, (t,s1,s2,sub), buffer):
        q = Perk(buffer[s1:s2].strip(), 'Ex', None)
        q.type = 'specialAC'
        self.specialQualities.append(q)

    def spells(self, (t,s1,s2,sub), buffer):
        q = Perk('spells', 'Sp', None)
        q.type = 'spells'
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)
        for part in ll:
            for k,v in part.items():
                setattr(q, k, v)

    def spellsLevel(self, (t,s1,s2,sub), buffer):
        l = buffer[s1:s2]
        l = re.search(r'(\d+)', l).group(1)
        return {'casterLevel': int(l)}

    def vulnerabilityArg(self, (t,s1,s2,sub), buffer):
        q = Perk('Vulnerability', 'Ex', None)
        q.type = 'vulnerability'
        q.damageType = buffer[s1:s2]
        self.specialQualities.append(q)

    def immunityArg(self, (t,s1,s2,sub), buffer):
        newQualities = []
        buf = buffer[s1:s2]
        if ' and ' in buf:
            imms = buf.split(' and ')
            for imm in imms:
                q = Perk('Immunity', 'Ex', None)
                q.type = 'immunity'
                q.damageType = imm.strip()
                newQualities.append(q)
        else:
            q = Perk('Immunity', 'Ex', None)
            q.type = 'immunity'
            q.damageType = buffer[s1:s2].strip()
            newQualities = [q]
        self.specialQualities.extend(newQualities)

    def resistanceName(self, (t,s1,s2,sub), buffer):
        q = Perk('Resistance', 'Ex', None)
        q.type = 'resistance'
        q.damageType = buffer[s1:s2].strip()
        self.specialQualities.append(q)

    def resistanceAmount(self, (t, s1, s2, sub), buffer):
        perk = self.specialQualities[-1]
        perk.amount = buffer[s1:s2]

    def regenerationArg(self, (t,s1,s2,sub), buffer):
        q = Perk('Regeneration', 'Ex', None)
        q.type = 'regeneration'
        q.amount = buffer[s1:s2]
        self.specialQualities.append(q)

    def damageReductionArg(self, (t,s1,s2,sub), buffer):
        q = Perk('Damage Reduction', 'Extraordinary', None)
        q.type = 'damageReduction'
        q.amount = buffer[s1:s2]
        self.specialQualities.append(q)

    def fastHealingArg(self, (t,s1,s2,sub), buffer):
        q = Perk('Fast Healing', 'Ex', None)
        q.type = 'fastHealing'
        q.amount = buffer[s1:s2]
        self.specialQualities.append(q)

    def empathyArg(self, (t,s1,s2,sub), buffer):
        q = Perk('Empathy', 'Ex', None)
        q.type = 'empathy'
        q.empathyType = buffer[s1:s2]
        self.specialQualities.append(q)

    def familyArg(self, (t,s1,s2,sub), buffer):
        q = Perk('Family Traits', None, None)
        q.type = 'family'
        q.familyName = buffer[s1:s2]
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
            q = Perk('Spell-like ability: %s' % (name,),
                    'Sp', None)
            q.type = 'spellLike'
            q.spell = name
            self.specialQualities.append(q)
        else:
            q = Perk(name, None, None)
            q.type = 'misc'
            self.specialQualities.append(q)
            for part in ll:
                for k,v in part.items():
                    setattr(q, k, v)

    def range(self, (t,s1,s2,sub), buffer):
        return {'range': buffer[s1:s2].strip()}

    def frightfulPresence(self, (t,s1,s2,sub), buffer):  
        q = Perk("Frightful presence", 'Ex', None)
        q.type = 'aura'
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)
        for part in ll:
            for k,v in part.items():
                setattr(q, k, v)

    def breathWeapon(self, (t,s1,s2,sub), buffer):
        q = Perk("Breath weapon", "Su", None)
        q.type = 'damaging'
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)

        for part in ll:
            if part:
                for k,v in part.items():
                    setattr(q, k, v)

    def breathEffect(self, *a, **kw):
        return {'breathEffect': disp.getString(*a, **kw).strip()}

    def breathPrismatic(self, *a, **kw):
        return {'breathEffect': disp.getString(*a, **kw).strip()}

    def summon(self, (t,s1,s2,sub), buffer):
        q = Perk('Summon', 'Sp', None)
        q.type = 'summon'
        self.specialQualities.append(q)

        ll = disp.dispatchList(self, sub, buffer)
        for part in ll:
            for k,v in part.items():
                setattr(q, k, v)

    def summonTarget(self, *a, **kw):
        return {'summonType': disp.getString(*a, **kw).strip()}

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


