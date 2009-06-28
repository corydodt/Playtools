"""
Parse treasures

"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

from playtools.common import C

grammar = ( # {{{
r'''# treasure stats
<ws>             :=  [ \t]*

<nonParen>       :=  letter/digit/whitespacechar/['"{}!@#*&^$%;:.,<>/?+-]

qualifier        :=  '(', nonParen*, ')'

aggregateType    :=  c'none'/c'standard'/c'double standard'/c'triple standard'/c'half standard'

aggregate        :=  aggregateType, ws, qualifier?

fraction         :=  '1/10'/'50%'/'1/5'/'1/4'/c'no'/c'standard'/c'double'

coins            :=  fraction, ws, c'coins', ws, qualifier?
goods            :=  fraction, ws, c'goods', ws, qualifier?
items            :=  fraction, ws, c'items', ws, qualifier?

specificItems    :=  printable*

>parts<          :=  coins, ';', ws, goods, ';', ws, items

treasureStat     :=  parts/aggregate, (';', specificItems)?
_treasureStat    :=  treasureStat
''') # }}}

treasureParser = parser.Parser(grammar, root="_treasureStat")


def parseTreasures(s):
    """
    Parse treasures in one of several forms, e.g. in aggregate: "double
    standard", in parts: "50% coins; standard goods; 50% items", and with
    either aggregate or per-part qualifiers "(nonflammable only)", and with
    appended extra items "; plus +3 longspeard".  Also accepts None for no
    treasure.
    """
    if s is None:
        s = "none"

    succ, children, end = treasureParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid treasure expression' % (s,))
    return children


class TreasurePart(object):
    """One of three monster treasure values
    """
    def __init__(self, name):
        self.name = name
        self.value = None
        self.qualifier = None

    def __repr__(self):
        return "<TreasurePart %s=%s>" % (self.name, self.value)


class Processor(disp.DispatchProcessor):
    def treasureStat(self, (t,s1,s2,sub), buffer):
        self._aggregate = False
        self.treasures = {}
        self.other = None
        disp.dispatchList(self, sub, buffer)
        return self.treasures, self.other

    def aggregateType(self, (t,s1,s2,sub), buffer):
        type = {'none': C.noTreasure,
                'standard': C.standardTreasure,
                'double standard': C.doubleStandardTreasure,
                'triple standard': C.tripleStandardTreasure,
                'half standard': C.halfStandardTreasure,
                }[disp.getString((t,s1,s2,sub), buffer).lower().strip()]
        self.treasures[C.Coins] = TreasurePart('coins')
        self.treasures[C.Coins].value = type
        self.treasures[C.Goods] = TreasurePart('goods')
        self.treasures[C.Goods].value = type
        self.treasures[C.Items] = TreasurePart('items')
        self.treasures[C.Items].value = type

    def aggregate(self, (t,s1,s2,sub), buffer):
        self._aggregate = True
        return disp.dispatchList(self, sub, buffer)

    def coins(self, (t,s1,s2,sub), buffer):
        self.currentTreasure = TreasurePart(C.Coins)
        self.treasures[C.Coins] = self.currentTreasure
        return disp.dispatchList(self, sub, buffer)

    def goods(self, (t,s1,s2,sub), buffer):
        self.currentTreasure = TreasurePart(C.Goods)
        self.treasures[C.Goods] = self.currentTreasure
        return disp.dispatchList(self, sub, buffer)

    def items(self, (t,s1,s2,sub), buffer):
        self.currentTreasure = TreasurePart(C.Items)
        self.treasures[C.Items] = self.currentTreasure
        return disp.dispatchList(self, sub, buffer)

    def qualifier(self, (t,s1,s2,sub), buffer):
        qualifier = disp.getString((t,s1,s2,sub), buffer)
        if self._aggregate:
            self.other = qualifier
        else:
            self.currentTreasure.qualifier = qualifier

    def fraction(self, (t,s1,s2,sub), buffer):
        frac = {'no': C.noTreasure,
                '1/10': '1/10',
                '1/5': '1/5',
                '1/4': '1/4',
                '50%': C.halfStandardTreasure,
                'standard': C.standardTreasure,
                'double': C.doubleStandardTreasure,
                }[disp.getString((t,s1,s2,sub), buffer).lower().strip()]
        self.currentTreasure.value = frac

    def specificItems(self, (t,s1,s2,sub), buffer):
        self.other = disp.getString((t,s1,s2,sub), buffer).lower().strip()


#
## proc = Processor()
## proc.currentTreasure=TreasurePart('coins')
## s = "double standard; plus +4 half-plate armor and gargantuan +3 adamantine warhammer"
## s = "standard coins; double goods; standard items; plus 1d4 magic weapons"
## print treasureParser.parse(s, processor=proc, production='_treasureStat')
