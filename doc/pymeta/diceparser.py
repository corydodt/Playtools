from pymeta.grammar import OMeta
from pymeta.runtime import ParseError

forward = ( # {{{ RPG-STYLE DICE EXPRESSIONS
r'''
ws               ::= <spaces>  
sign             ::= ('+' | '-')
digits           ::= (<digit>+):n                  => int(''.join(n))
signed           ::= <sign>:s <ws> <digits>:c      => int('%s%s' % (s, c))
                                               
dieSize          ::= 'd' <ws> <digits>:d           => sa('dieSize', d)
count            ::= <digits>:c                    => sa('count', c)
dieSet           ::= <count>? <ws> <dieSize>
                                               
filter           ::= (('h' | 'H' | 'l' | 'L'):fd   => sa('filterDirection', fd.lower())
                      <digits>:fc                  => sa('filterCount', fc)
                      )
                                               
dieModifier      ::= <signed>:s                    => sa('dieModifier', s)
                                               
repeat           ::= <digits>:r                    => sa('repeat', r)
sorted           ::= <token 'sort'>                => sa('sort', 'sort')
rollRepeat       ::= 'x' <ws> <repeat> <ws> <sorted>?

randomNumber     ::= <dieSet> <ws> <filter>?
staticNumber     ::= <digits>:n <ws> ~'d'          => sa('staticNumber', int(n))
generatedNumber  ::= (<staticNumber> | <randomNumber>)

diceExpression   ::= <ws> <generatedNumber> <dieModifier>? <ws> <rollRepeat>? ~~(<anything>?):ws ?(nothing(ws))
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

    def nothing(self, data):
        """
        True if data is None or contains only whitespace
        """
        return data is None or data.strip() == ''

    @classmethod
    def fromString(cls, s):
        """
        Build a DiceExpression by parsing a string
        """
        dexp = cls()
        sa = lambda k, v: setattr(dexp, k, v)
        embedded = {'sa':sa, 'nothing': dexp.nothing}
        g = OMeta.makeGrammar(forward, embedded, name="DiceExpression")
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
        return self.format()

    def format(self):
        if self.staticNumber is None:
            # minimize by dropping clauses that are defaults

            # no filter if self.filterCount is None
            filter = u''
            if self.filterCount is not None:
                filter = u'%s%d' % (self.filterDirection, self.filterCount)

            # no modifier if +0
            modifier = u''
            if self.dieModifier != 0:
                modifier = u'%+d' % (self.dieModifier,)

            # no repeat if x1
            repeat = u''
            if self.repeat > 1:
                repeat = u'x%d' % (self.repeat,)

            # no count if == 1
            count = u''
            if self.count != 1:
                count = self.count
            return u'%sd%d%s%s%s%s' % (count, self.dieSize, filter, modifier, repeat, self.sort)
        else:
            return u'%s' % (self.staticNumber,)


def parseDice(s):
    try:
        ret = DiceExpression.fromString(s)
    except ParseError, p:
        raise RuntimeError('%s is not a valid dice expression' % (s,))
    return ret 

