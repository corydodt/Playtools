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

qualifier              :=  '(', nonParen*, ')'

trueAlignment          :=  c'lawful good'/c'neutral good'/c'chaotic good'/c'lawful neutral'/c'chaotic neutral'/c'lawful evil'/c'neutral evil'/c'chaotic evil'/c'neutral'/c'none'

atom                   :=  c'lawful'/c'chaotic'/c'evil'/c'good'

>always<               :=  c'always', !, ws, trueAlignment, ws

usuallyOftenQualifier  :=  c'usually'/c'often'
>usuallyOften<         :=  usuallyOftenQualifier, !, ws, trueAlignment, ws
>rawAlignment<         :=  trueAlignment 

oneAlignment           :=  always/usuallyOften/rawAlignment

>choice<               :=  oneAlignment, (ws, 'or', !, ws, oneAlignment)*, ws
any                    :=  c'any', !, (ws, atom)?, ws

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
    alignment = None
    qualifier = None

    def simplify(self):
        """
        A flat list version of the alignment
        """
        r = []
        if self.alignment is not None:
            r.append(self.alignment)
        if self.qualifier is not None and len(self.qualifier) > 0:
            r.append(''.join(self.qualifier))
        return r



class Processor(disp.DispatchProcessor):
    def alignmentStat(self, (t,s1,s2,sub), buffer):
        self.alignments = []
        self.currentAlignment = None
        disp.dispatchList(self, sub, buffer)
        return [x.simplify() for x in self.alignments]

    def atom(self, (t,s1,s2,sub), buffer):
        self.currentAlignment.alignment = atomMap[
                disp.getString((t,s1,s2,sub),buffer).lower().strip()
                ]

    def any(self, (t,s1,s2,sub), buffer):
        self.currentAlignment = AlignmentPart()
        disp.dispatchList(self, sub, buffer)
        possibles = atomCross[self.currentAlignment.alignment]
        for p in possibles:
            al = AlignmentPart()
            al.alignment = p
            al.qualifier = self.currentAlignment.qualifier
            self.alignments.append(al)
        self.currentAlignment = None

    def trueAlignment(self, (t,s1,s2,sub), buffer):
        self.currentAlignment.alignment = alignMap[
                disp.getString((t,s1,s2,sub),buffer).lower()
                ]

    def usuallyOftenQualifier(self, (t,s1,s2,sub), buffer):
        self.currentAlignment.qualifier.append(
                disp.getString((t,s1,s2,sub), buffer)
                )

    def oneAlignment(self, (t,s1,s2,sub), buffer):
        self.currentAlignment = AlignmentPart()
        self.currentAlignment.qualifier = []
        disp.dispatchList(self, sub, buffer)
        self.alignments.append(self.currentAlignment)
        self.currentAlignment = None

    def qualifier(self, (t,s1,s2,sub), buffer):
        qualifier = disp.getString((t,s1,s2,sub), buffer)
        self.currentAlignment.qualifier.append(qualifier)


#
## proc = Processor()
## proc.currentAlignment=AlignmentPart('coins')
## s = "double standard; plus +4 half-plate armor and gargantuan +3 adamantine warhammer"
## s = "standard coins; double goods; standard items; plus 1d4 magic weapons"
## print alignmentParser.parse(s, processor=proc, production='_alignmentStat')
