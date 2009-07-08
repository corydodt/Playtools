"""
Parse alignments

"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

from playtools.common import C

grammar = ( # {{{
r'''# alignment stats
<ws>                   :=  [ \t]*

<nonParen>             :=  letter/digit/whitespacechar/['"{}!@#*&^$%;:.,<>/?+-]

qualifier              :=  c'usually'/c'often'/('(', nonParen*, ')')
postqualifier          :=  qualifier

trueAlignment          :=  c'lawful good'/c'neutral good'/c'chaotic good'/c'lawful neutral'/c'chaotic neutral'/c'lawful evil'/c'neutral evil'/c'chaotic evil'/c'neutral'/c'none'

atom                   :=  c'lawful'/c'chaotic'/c'evil'/c'good'

>always<               :=  c'always', !, ws, trueAlignment, ws

>usuallyOften<         :=  qualifier, !, ws, always/trueAlignment/any, ws
oneAlignment           :=  usuallyOften/always/trueAlignment, (ws, postqualifier)?

>choice<               :=  oneAlignment, (ws, 'or', !, ws, oneAlignment)*, ws
any                    :=  c'any', !, (ws, atom)?, (ws, qualifier)?, ws

alignmentStat          :=  choice/any
_alignmentStat         :=  alignmentStat
''') # }}}

alignmentParser = parser.Parser(grammar, root="_alignmentStat")

alignMap = {'lawful good': C.lawfulGood,
        'neutral good': C.neutralGood,
        'chaotic good': C.chaoticGood,
        'lawful neutral': C.lawfulNeutral,
        'neutral': C.neutralNeutral,
        'chaotic neutral': C.chaoticNeutral,
        'lawful evil': C.lawfulEvil,
        'neutral evil': C.neutralEvil,
        'chaotic evil': C.chaoticEvil,
        'none': C.noAlignment,
        }

atomMap = {'lawful': C.lawful, 
        'chaotic': C.chaotic, 
        'good': C.good,
        'evil': C.evil,
        '': None,
        }

# for each atom, given "any", all the possible alignments
atomCross = {C.lawful: [C.lawfulGood, C.lawfulNeutral, C.lawfulEvil],
        C.chaotic: [C.chaoticGood, C.chaoticNeutral, C.chaoticEvil],
        C.good: [C.lawfulGood, C.neutralGood, C.chaoticGood],
        C.evil: [C.lawfulEvil, C.neutralEvil, C.chaoticEvil],
        None: [C.lawfulGood, C.neutralGood, C.chaoticGood, C.lawfulEvil, C.neutralEvil, C.chaoticEvil,
            C.lawfulNeutral, C.neutralNeutral, C.chaoticNeutral, ],
        }


def parseAlignment(s):
    """
    Parse alignments in one of several forms, e.g. in aggregate: "double
    standard", in parts: "50% coins; standard goods; 50% items", and with
    either aggregate or per-part qualifiers "(nonflammable only)", and with
    appended extra items "; plus +3 longspeard".  Also accepts None for no
    alignment.
    """
    if s is None:
        s = "always none"

    succ, children, end = alignmentParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid alignment expression' % (s,))
    return children[0]


class AlignmentPart(object):
    """
    A container for an alignment choice
    """
    def __init__(self, id):
        self.id = id
        self.qualifiers = []

    def simplify(self):
        """
        A flat list version of the alignment
        """
        r = []
        if self.id is not None:
            r.append(self.id)
        if len(self.qualifiers) > 0:
            r.append('; '.join(self.qualifiers))
        return r


class Processor(disp.DispatchProcessor):
    def alignmentStat(self, (t,s1,s2,sub), buffer):
        self.alignments = []
        self.qualifiers = None
        self.currentAtom = None
        disp.dispatchList(self, sub, buffer)
        return [x.simplify() for x in self.alignments]

    def oneAlignment(self, (t,s1,s2,sub), buffer):
        self.qualifiers = []
        disp.dispatchList(self, sub, buffer)

    def atom(self, (t,s1,s2,sub), buffer):
        atom = disp.getString((t,s1,s2,sub),buffer).lower().strip()
        self.currentAtom = atomMap[ atom ]

    def any(self, (t,s1,s2,sub), buffer):
        if self.qualifiers is None:
            self.qualifiers = []
        disp.dispatchList(self, sub, buffer)
        array = atomCross[self.currentAtom]
        for id in array:
            self.gotCompleteAlignment(id)

    def gotCompleteAlignment(self, id):
        """
        We have identified a complete alignment.  add it to self.alignments
        """
        part = AlignmentPart(id)
        self.alignments.append(part)
        if self.qualifiers is not None:
            assert part.qualifiers == []
            part.qualifiers = self.qualifiers[:]

    def trueAlignment(self, (t,s1,s2,sub), buffer):
        id = alignMap[ disp.getString((t,s1,s2,sub),buffer).lower() ]
        self.gotCompleteAlignment(id)

    def qualifier(self, (t,s1,s2,sub), buffer):
        q = disp.getString((t,s1,s2,sub), buffer)
        self.qualifiers.append(q)

    def postqualifier(self, (t,s1,s2,sub), buffer):
        q = disp.getString((t,s1,s2,sub), buffer)[1:-1]
        for al in self.alignments:
            al.qualifiers.append(q)


#
## proc = Processor()
## ## proc.currentAlignment = AlignmentPart()
## s = "Usually any evil"
## ## s = "standard coins; double goods; standard items; plus 1d4 magic weapons"
## ## print alignmentParser.parse(s, processor=proc, production='_alignmentStat')[1]
## print parseAlignment(s)
