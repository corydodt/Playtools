"""
Parse armor classes
"""
import re

from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

from playtools.test.pttestutil import TODO

grammar = ( # {{{
r'''# armorclass stats
<ws>               :=  [ \t]*

<nonParen>         :=  letter/digit/whitespacechar/['"{}!@#*&^$%;:.,<>/?+-]/'['/']'
<otherArmorName>   :=  letter/digit/whitespacechar/['.+-]/'['/']'

splat              :=  '*'  

qualifier          :=  '(', nonParen*, ')'

amount             :=  '+'/'-', !, int

flatFooted         :=  'flat-footed', !, ws, int

touch              :=  'touch', !, ws, int

other              :=  amount, ws, otherArmorName+, splat?
natural            :=  amount, ws, c'natural', splat?
deflection         :=  amount, ws, c'deflection', splat?
dex                :=  amount, ws, c'dex', splat?
size               :=  amount, ws, c'size', splat?
>armorPart<        :=  size/dex/deflection/natural/other
>math<             :=  '(', !, armorPart, (', ', armorPart)*, ')'

total              :=  digit+

>armorclassStat1<  :=  total, ws, math, ',', ws, touch, ',', ws, flatFooted
armorclassStat     :=  armorclassStat1, (',', ws, 'or', ws, qualifier)?
_armorclassStat    :=  armorclassStat
''') # }}}

armorclassParser = parser.Parser(grammar, root="_armorclassStat")


def parseArmor(s):
    """
    Parse armorclass
    """
    succ, children, end = armorclassParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid armorclass expression' % (s,))
    return children


class ArmorClass(object):
    """A fully parsed armor class
    """
    __slots__ = ['value', 'qualifier', 'dexBonus', 'natural', 'deflection',
                 'otherArmor', 'size', 'body', 'shield', 'touch',
                 'flatFooted'
                 ]
    def __init__(self):
        self.value = 0
        self.qualifier = None
        self.dexBonus = 0
        self.natural = 0
        self.deflection = 0
        self.otherArmor = ()
        self.size = 0
        self.body = (None, None)
        self.shield = (None, None)
        self.touch = None
        self.flatFooted = None


class Processor(disp.DispatchProcessor):
    def armorclassStat(self, (t,s1,s2,sub), buffer):
        self.armorclass = ArmorClass()
        disp.dispatchList(self, sub, buffer)
        return self.armorclass

    def splat(self, *a, **kw):
        if self.armorclass.qualifier is None:
            self.armorclass.qualifier = ''
        self.armorclass.qualifier += '*'

    def qualifier(self, (t,s1,s2,sub), buffer):
        if self.armorclass.qualifier is None:
            self.armorclass.qualifier = ''
        self.armorclass.qualifier += disp.getString((t,s1+1, s2-1, sub),
                buffer)

    def total(self, *a, **kw):
        self.armorclass.value = int(disp.getString(*a, **kw))

    def size(self, (t,s1,s2,sub), buffer):
        self.armorclass.size = disp.dispatchList(self, sub, buffer)[0]

    def dex(self, (t,s1,s2,sub), buffer):
        self.armorclass.dexBonus = disp.dispatchList(self, sub, buffer)[0]

    def flatFooted(self, (t,s1,s2,sub), buffer):
        s = disp.getString((t,s1,s2,sub), buffer)
        self.armorclass.flatFooted = int(s.split()[-1])
        
    def touch(self, (t,s1,s2,sub), buffer):
        s = disp.getString((t,s1,s2,sub), buffer)
        self.armorclass.touch = int(s.split()[-1])
        
    def amount(self, *a, **kw):
        return int(disp.getString(*a, **kw))
        
    def deflection(self, (t,s1,s2,sub), buffer):
        self.armorclass.deflection = disp.dispatchList(self, sub, buffer)[0]

    def natural(self, (t,s1,s2,sub), buffer):
        self.armorclass.natural = disp.dispatchList(self, sub, buffer)[0]

    def other(self, (t,s1,s2,sub), buffer):
        s = disp.getString((t,s1,s2,sub), buffer)
        num, rest = s.split(None, 1)
        num = int(num)
        if 'shield' in s or 'buckler' in s:
            assert self.armorclass.shield == (None, None)
            self.armorclass.shield = (num, rest)
            return
            """
            +1 buckler
            +1 light shield
            +1 light wooden shield
            +2 heavy shield
            +2 heavy steel shield
            """

        if ('armor' in s or 'hide' in s or 'leather' in s or
                'plate' in s or 'chain' in s or 'mail' in s or
                'bracers' in s):
            assert self.armorclass.body == (None, None)
            self.armorclass.body = (num, rest)
            return
            """
            +10 +2 full plate armor
            +12 armor [+5 half plate]
            +2 leather armor
            +3 hide
            +3 hide armor
            +3 studded leather
            +3 studded leather armor
            +4 chain shirt
            +4 scale mail
            +5 breastplate
            +5 chainmail
            +6 banded mail
            +7 half-plate armor
            +8 bracers
            +8 bracers of armor
            """

        if self.armorclass.otherArmor == ():
            self.armorclass.otherArmor = []
        self.armorclass.otherArmor.append((num, rest))

