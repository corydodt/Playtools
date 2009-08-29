from pymeta.grammar import OMeta
from pymeta.runtime import ParseError

forward = ( # {{{ RPG-STYLE DICE EXPRESSIONS
r'''
sign             ::= ('+' | '-')
digits           ::= (<digit>+):n                  => int(''.join(n))
signed           ::= <sign>:s <spaces> <digits>:c  => int('%s%s' % (s, c))
                                               
dieSize          ::= 'd' <spaces> <digits>:d       => sa('dieSize', d)
count            ::= <digits>:c                    => sa('count', c)
dieSet           ::= <count>? <spaces> <dieSize>
                                               
filter           ::= (('h' | 'H' | 'l' | 'L'):fd   => sa('filterDirection', fd.lower())
                      <digits>:fc                  => sa('filterCount', fc)
                      )
                                               
dieModifier      ::= <signed>:s                    => sa('dieModifier', s)
                                               
repeat           ::= <digits>:r                    => sa('repeat', r)
sorted           ::= <token 'sort'>                => sa('sort', 'sort')
rollRepeat       ::= 'x' <spaces> <repeat> <spaces> <sorted>?

randomNumber     ::= <dieSet> <spaces> <filter>?
staticNumber     ::= <digits>:n <spaces> ~'d'      => sa('staticNumber', int(n))
generatedNumber  ::= (<staticNumber> | <randomNumber>)

diceExpression  ::= <spaces> <generatedNumber> <dieModifier>? <spaces> <rollRepeat>? <spaces>
''') # }}}


class DiceExpression(object):
    def __init__(self):
        self.count = 1
        self.dieSize = 1
        self.dieModifier = 0
        self.repeat = 1
        self.sort = ''
        self.filterDirection = None
        self.filterCount = None
        self.staticNumber = None

    @classmethod
    def fromString(cls, s):
        """
        Build a DiceExpression by parsing a string
        """
        dexp = cls()
        sa = lambda k, v: setattr(dexp, k, v)
        g = OMeta.makeGrammar(forward, {'sa': sa}, name="DiceExpression")
        g(s).apply('diceExpression')
        return dexp

    def toList(self):
        """
        Produce a listing of my dice properties
        """
        return [self.staticNumber, self.count, self.dieSize,
                self.filterDirection, self.filterCount, self.dieModifier,
                self.repeat, self.sort]

    def formatNone(self, o):
        return '' if o is None else str(o)

    def repList(self):
        """
        Produce a stringy version of this 
        """
        fn = self.formatNone
        ll = self.toList()
        return 'sn=%s c=%s ds=%s fd=%s fc=%s dm=%s r=%s sort=%s' % tuple(map(fn, ll))

    def __str__(self):
        if self.staticNumber is None:
            # minimize by dropping clauses that are defaults

            # no filter if self.filterCount is None
            filter = ''
            if self.filterCount is not None:
                filter = '%s%d' % (self.filterDirection, self.filterCount)

            # no modifier if +0
            modifier = ''
            if self.dieModifier != 0:
                modifier = '%+d' % (self.dieModifier,)

            # no repeat if x1
            repeat = ''
            if self.repeat > 1:
                repeat = 'x%d' % (self.repeat,)

            # no count if == 1
            count = ''
            if self.count != 1:
                count = self.count
            return '%sd%d%s%s%s%s' % (count, self.dieSize, filter, modifier, repeat, self.sort)
        else:
            return str(self.staticNumber)


def parseDice(s):
    try:
        ret = DiceExpression.fromString(s)
    except ParseError, p:
        raise RuntimeError('%s is not a valid dice expression' % (s,))
    return ret 

