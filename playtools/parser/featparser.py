"""
Parse feats in the form:

    Foo, Weapon Specialization (katana, club), Improved Sunder

... etc.

"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers
## appease pyflakes
numbers


grammar = ( # {{{
r'''# feats aplenty
<ws> := [ \t]*
<nameChar> := [][-0-9a-zA-Z'" \t]
<name> := nameChar+

empty := '-'

>featList< := feat, (',', ws, !, feat)*

<subFeatName> := name
timesTaken   := '(', 'x', !, int, ')'
subFeatGroup := '(', !, name, (',', ws, !, name)*, ')'

baseFeatName := name
>feat< := baseFeatName, (timesTaken/subFeatGroup)?

featStat := empty/featList
featStatRoot := featStat
''' ) # }}}


featParser = parser.Parser(grammar, root='featStatRoot')


class Feat(object):
    qualifier = None
    timesTaken = None

    def __repr__(self):
        return '<%s>' % (str(self),)

    def __str__(self):
        q = ''
        if self.qualifier is not None:
            q = ' (%s)' % (self.qualifier,)
        return '%s%s' % (self.name, q)


class Processor(disp.DispatchProcessor):
    def featStat(self, (t,s1,s2,sub), buffer):
        self.feats = []
        disp.dispatchList(self, sub, buffer)
        return self.feats

    def empty(self, *a, **kw):
        pass

    def baseFeatName(self, (t,s1,s2,sub), buffer):
        self.currentFeat = Feat()
        self.feats.append(self.currentFeat)
        self.currentFeat.name = disp.getString((t,s1,s2,sub), buffer).strip()

    def timesTaken(self, (t,s1,s2,sub), buffer):
        s = disp.getString((t,s1+1,s2-1,sub), buffer).strip()
        self.currentFeat.timesTaken = int(s[1:])

    def subFeatGroup(self, (t,s1,s2,sub), buffer):
        s = disp.getString((t,s1+1,s2-1,sub), buffer).strip()
        self.currentFeat.qualifier = s


def parseFeats(s):
    if not s:
        return None
    succ, children, end = featParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid feat expression' % (s,))
    return children

