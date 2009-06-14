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
subFeatGroup := '(', !, name, (',', ws, !, name)*, ')'

baseFeatName := name
>feat< := baseFeatName, subFeatGroup?

featStat := empty/featList
featStatRoot := featStat
''' ) # }}}


featParser = parser.Parser(grammar, root='featStatRoot')


class Feat(object):
    def __init__(self):
        self.qualifier = None

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

    def subFeatGroup(self, (t,s1,s2,sub), buffer):
        self.currentFeat.qualifier = disp.getString((t,s1+1,s2-1,sub),
                buffer).strip()


def parseFeats(s):
    succ, children, end = featParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid feat expression' % (s,))
    return children



tests = ( # {{{
"""-
Ability Focus (poison), Alertness, Flyby Attack
Iron Will, Toughness (2)
Alertness, Empower Spell, Flyby Attack, Hover, Improved Initiative, Maximize Spell, Power Attack, Weapon Focus (bite), Weapon Focus (claw), Wingover
Alertness, Improved Critical (chain), Improved Initiative
Multiattack, Toughness
Cleave, Improved Sunder, Iron Will, Multiattack, Power Attack, Weapon Focus (spiked chain)
Alertness, Iron Will, Track
Blind-Fight, Cleave, Combat Reflexes, Improved Initiative, Power Attack
Great Fortitude, Ride-by Attack, Spirited Charge
Alertness, Combat Reflexes, Improved Initiative, Skill Focus (Sense Motive), Skill Focus (Survival), Stealthy, Track
Alertness, Toughness
Weapon Focus (rapier)
Alertness
Alertness, Diehard, Endurance, Toughness (2)
Flyby Attack, Improved Initiative, Improved Critical (bite), Iron Will, Multiattack, Weapon Focus (eye ray), Weapon Focus (bite)
Alertness, Empower Spell, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Alertness, Hover, Improved Initiative, Weapon Focus (bite)
Alertness, Weapon Focus (morningstar)
Alertness, Empower Spell, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Alertness, Awesome Blow, Blind-Fight, Cleave, Combat Reflexes, Dodge, Great Cleave, Improved Bull Rush, Improved Initiative, Iron Will, Power Attack, Toughness (6)
Weapon Focus (longbow), item creation feat (any one)
Alertness, Blind-Fight, Cleave, Empower Spell, Flyby Attack, Hover, Improved Initiative, Maximize Spell, Power Attack, Snatch, Weapon Focus (bite), Weapon Focus (claw), Wingover
Alertness, Empower Spell, Flyby Attack, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Lycanthrope Hybrid Feats (same as human form)
""".splitlines()) # }}}

if __name__ == '__main__':
    for flist in tests:
        print flist
        parsed = parseFeats(flist)
        print parsed
