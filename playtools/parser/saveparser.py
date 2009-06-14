"""
Parse saves in the form:

    Fort +1, Ref -, Will +2*

... etc.

"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

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

class SaveStat(object):
    """The set of saves owned by a monster
    
    FIXME - this is identical to abilityparser.AbilityStat
    """
    def __init__(self, name):
        self.name = name
        self.bonus = 0
        self.qualifier = ''
        self.splat = ''
        self.other = None

    def __repr__(self):
        if self.other is not None:
            return "<SaveStat %s>" % (self.other,)
        return "<SaveStat %s=%s>" % (self.name, self.bonus)

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
    def other(self, (t,s1,s2,sub), buffer):
        fort = SaveStat('fort')
        fort.other = buffer
        ref = SaveStat('ref')
        ref.other = buffer
        will = SaveStat('will')
        will.other = buffer
        return dict(fort=fort, ref=ref, will=will)

    def saveList(self, (t,s1,s2,sub), buffer):
        self.saves = {}
        disp.dispatchList(self, sub, buffer)
        return self.saves

    def undefined(self, (t,s1,s2,sub), buffer):
        self.currentSave.other = disp.getString((t,s1,s2,sub), buffer)

    def fort(self, (t,s1,s2,sub), buffer):
        self.currentSave = SaveStat('fort')
        self.saves['fort'] = self.currentSave
        return disp.dispatchList(self, sub, buffer)

    def ref(self, (t,s1,s2,sub), buffer):
        self.currentSave = SaveStat('ref')
        self.saves['ref'] = self.currentSave
        return disp.dispatchList(self, sub, buffer)

    def will(self, (t,s1,s2,sub), buffer):
        self.currentSave = SaveStat('will')
        self.saves['will'] = self.currentSave
        return disp.dispatchList(self, sub, buffer)

    def bonus(self, (t,s1,s2,sub), buffer):
        self.currentSave.bonus = int(buffer[s1:s2]) 

    def splat(self, (t,s1,s2,sub), buffer):
        self.currentSave.splat = '*'

    def qualifier(self, (t,s1,s2,sub), buffer):
        self.currentSave.qualifier = disp.getString((t,s1,s2,sub), buffer)

