from simpleparse import parser, dispatchprocessor as disp, objectgenerator
from simpleparse.common import numbers
## appease pyflakes
numbers


grammar = ( # {{{
r'''# RPG-STYLE DICE EXPRESSIONS
<ws> := [ \t]*
<n> := int
<ds> := digits
<sign> := [-+]
<comma_number> := (digit/',')+

dieSize := 'd',ws,n
count := n
dieSet := count?,ws,dieSize

filter := [hHlL], ds

# this looks like int, but the ws is not parsed correctly by int
dieModifier := sign,ws,comma_number

repeat := n
sorted := 'sort'
rollRepeat := 'x',ws,repeat,ws,sorted?

randomNumber := dieSet,ws,filter?
staticNumber := n,ws,?-'d'

>generatedNumber< := staticNumber/randomNumber

diceExpression := generatedNumber,dieModifier?,ws,rollRepeat?

# normally my root production will not get called in the Processor,
# so define a dummy root around it, and then it will
diceExpressionRoot := ws,diceExpression
''') # }}}


class DiceExpression(object):
    def __init__(self):
        self.count = 1
        self.dieSize = 1
        self.dieModifier = 0
        self.repeat = 1
        self.sort = ''
        self.filterDirection = 'h'
        self.filterCount = None
        self.staticNumber = None

    def __repr__(self):
        return '<DiceExpression %s>' % (str(self),)

    def __str__(self):
        if self.staticNumber is None:
            # minimize by dropping clauses that are defaults

            # no filter if self.filterCount is None
            filter = ''
            if self.filterCount is not None:
                filter = '%s%d' % (self.filterDirection, self.filterCount)

            # no modifier if +0
            modifier = ''
            if self.dieModifier > 0:
                modifier = '%+d' % (self.dieModifier,)

            # no repeat if x1
            repeat = ''
            if self.repeat > 1:
                repeat = 'x%d' % (self.repeat,)

            return '%dd%d%s%s%s%s' % (self.count, self.dieSize,
                    filter, modifier, repeat, self.sort)
        else:
            return str(self.staticNumber)


class Processor(disp.DispatchProcessor):
    def diceExpression(self, (t,s1,s2,sub), buffer):
        self.expr = DiceExpression()
        disp.dispatchList(self, sub, buffer)
        return self.expr

    def randomNumber(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def staticNumber(self, (t,s1,s2,sub), buffer):
        self.expr.staticNumber = int(buffer[s1:s2])

    def dieSet(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def sorted(self, (t,s1,s2,sub), buffer):
        self.expr.sort = 'sort'

    def filter(self, (t,s1,s2,sub), buffer):
        self.expr.filterDirection = buffer[s1].lower()
        self.expr.filterCount = int(buffer[s1+1:s2])

    def count(self, (t,s1,s2,sub), buffer):
        self.expr.count = int(buffer[s1:s2])

    def dieModifier(self, (t,s1,s2,sub), buffer):
        n = buffer[s1:s2].replace(',', '')
        self.expr.dieModifier = int(n)

    def dieSize(self, (t,s1,s2,sub), buffer):
        self.expr.dieSize = int(buffer[s1+1:s2])

    def repeat(self, (t,s1,s2,sub), buffer):
        self.expr.repeat = int(buffer[s1:s2])

    def rollRepeat(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)


diceParser = parser.Parser(grammar, root="diceExpressionRoot")


def parseDice(s):
    succ, children, end = diceParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid dice expression' % (s,))
    return children


def reverseFormatDice(parsed_dice):
    """Take a parsed dice expression and return the string form"""
    p = parsed_dice[0]
    _dice_expr = []
    if p.staticNumber:
        return str(p.staticNumber)
    if p.count and p.count != 1:
        _dice_expr.append(str(p.count))
    if p.dieSize:
        _dice_expr.append('d' + str(p.dieSize))
    if p.filterCount:
        _dice_expr.append(str(p.filterDirection))
        _dice_expr.append(str(p.filterCount))
    if p.dieModifier:
        _dice_expr.append('%+d' % (p.dieModifier,))
    if p.repeat and p.repeat != 1:
        _dice_expr.append('x' + str(p.repeat))
    if p.sort:
        _dice_expr.append('sort')
    return ''.join(_dice_expr)


diceExpression = objectgenerator.LibraryElement(
		generator = diceParser._generator,
		production = 'diceExpression',
        )

