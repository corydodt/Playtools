"""
Parse saves in the form:

    Fort +1, Ref -, Will +2*

... etc.

"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

from abilityparser import NumericStatWithQualifier

grammar = ( # {{{
r'''# saving throw stats
<ws> := [ \t]*
<n> := int
splat := '*'
<p> := printable

undefined := '-', ?-n

<nonParen> := letter/digit/whitespacechar/['"{}!@#*&^$%;:.<>/?+-]

qualifier := '(', nonParen*, ')'

bonus := n

>value< := undefined/bonus, splat?, ws, qualifier?

fort := 'Fort', ws, value
ref := 'Ref', ws, value
will := 'Will', ws, value

saveList := fort, ',', ws, ref, ',', ws, will 

other := ?-('Fort'), p

saveStat := other/saveList
''') # }}}

saveParser = parser.Parser(grammar, root="saveStat")

def parseSaves(s):
    succ, children, end = saveParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid save expression' % (s,))
    return children


class Processor(disp.DispatchProcessor):
    def other(self, (t,s1,s2,sub), buffer):
        fort = NumericStatWithQualifier('fort')
        fort.other = buffer
        ref = NumericStatWithQualifier('ref')
        ref.other = buffer
        will = NumericStatWithQualifier('will')
        will.other = buffer
        return dict(fort=fort, ref=ref, will=will)

    def saveList(self, (t,s1,s2,sub), buffer):
        self.saves = {}
        disp.dispatchList(self, sub, buffer)
        return self.saves

    def undefined(self, (t,s1,s2,sub), buffer):
        self.currentSave.other = disp.getString((t,s1,s2,sub), buffer)

    def fort(self, (t,s1,s2,sub), buffer):
        self.currentSave = NumericStatWithQualifier('fort')
        self.saves['fort'] = self.currentSave
        return disp.dispatchList(self, sub, buffer)

    def ref(self, (t,s1,s2,sub), buffer):
        self.currentSave = NumericStatWithQualifier('ref')
        self.saves['ref'] = self.currentSave
        return disp.dispatchList(self, sub, buffer)

    def will(self, (t,s1,s2,sub), buffer):
        self.currentSave = NumericStatWithQualifier('will')
        self.saves['will'] = self.currentSave
        return disp.dispatchList(self, sub, buffer)

    def bonus(self, (t,s1,s2,sub), buffer):
        self.currentSave.bonus = int(buffer[s1:s2]) 

    def splat(self, (t,s1,s2,sub), buffer):
        self.currentSave.splat = '*'

    def qualifier(self, (t,s1,s2,sub), buffer):
        self.currentSave.qualifier = disp.getString((t,s1,s2,sub), buffer)

