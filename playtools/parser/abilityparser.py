"""
The "pure" abilities need to be parsed, e.g. str int dex con cha wis
"""

from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

grammar = ( # {{{
r'''# ability stats
<ws> := [ \t]*
<n> := int
splat := '*'
<p> := printable

undefined := '-', ?-n

<nonParen> := letter/digit/whitespacechar/['"{}!@#*&^$%;:.<>/?+-]

qualifier := '(', nonParen*, ')'

bonus := n

>value< := undefined/bonus, splat?, ws, qualifier?

strn := 'Str', ws, value
dext := 'Dex', ws, value
cons := 'Con', ws, value
intl := 'Int', ws, value
wisd := 'Wis', ws, value
chas := 'Cha', ws, value

abList := strn, ',', ws, dext, ',', ws, cons, ',', ws, intl, ',', ws, wisd, ',', ws, chas

abStat := abList
''') # }}}

#       t1 = "Str 9, Dex 10, Con 11, Int 12, Wis 13, Cha 14"


abParser = parser.Parser(grammar, root="abStat")

def parseAbilities(s):
    succ, children, end = abParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid ability expression' % (s,))
    return children


class AbilityStat(object):
    """The set of abilities owned by a monster
    
    FIXME - this is identical to saveparser.SaveStat
    """
    def __init__(self, name):
        self.name = name
        self.bonus = 0
        self.qualifier = ''
        self.splat = ''
        self.other = None

    def __repr__(self):
        if self.other is not None:
            return "<AbilityStat %s>" % (self.other,)
        return "<AbilityStat %s=%s>" % (self.name, self.bonus)

    def __str__(self):
        if self.other:
            return '(%s)' % (self.other,)
        else:
            splat = ''
            qual = ''

            if self.splat:
                splat = '*'

            if self.qualifier:
                qual = ' %s' % (self.qualifier,)

            if self.bonus:
                return '%+d%s%s' % (self.bonus, splat, qual)
            else:
                return '-%s%s' % (splat, qual)


class Processor(disp.DispatchProcessor):
    def abList(self, (t,s1,s2,sub), buffer):
        self.abilities = {}
        disp.dispatchList(self, sub, buffer)
        return self.abilities

    def strn(self, (t,s1,s2,sub), buffer):
        self.currentAbility = AbilityStat('str')
        self.abilities['str'] = self.currentAbility
        return disp.dispatchList(self, sub, buffer)

    def dext(self, (t,s1,s2,sub), buffer):
        self.currentAbility = AbilityStat('dex')
        self.abilities['dex'] = self.currentAbility
        return disp.dispatchList(self, sub, buffer)

    def cons(self, (t,s1,s2,sub), buffer):
        self.currentAbility = AbilityStat('con')
        self.abilities['con'] = self.currentAbility
        return disp.dispatchList(self, sub, buffer)

    def intl(self, (t,s1,s2,sub), buffer):
        self.currentAbility = AbilityStat('int')
        self.abilities['int'] = self.currentAbility
        return disp.dispatchList(self, sub, buffer)

    def wisd(self, (t,s1,s2,sub), buffer):
        self.currentAbility = AbilityStat('wis')
        self.abilities['wis'] = self.currentAbility
        return disp.dispatchList(self, sub, buffer)

    def chas(self, (t,s1,s2,sub), buffer):
        self.currentAbility = AbilityStat('cha')
        self.abilities['cha'] = self.currentAbility
        return disp.dispatchList(self, sub, buffer)

    def undefined(self, (t,s1,s2,sub), buffer):
        self.currentAbility.other = disp.getString((t,s1,s2,sub), buffer)

    def splat(self, (t,s1,s2,sub), buffer):
        self.currentAbility.splat = '*'

    def bonus(self, (t,s1,s2,sub), buffer):
        self.currentAbility.bonus = int(buffer[s1:s2]) 

    def qualifier(self, (t,s1,s2,sub), buffer):
        self.currentAbility.qualifier = disp.getString((t,s1,s2,sub), buffer)

