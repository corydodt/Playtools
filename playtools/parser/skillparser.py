"""
Parse skills in the form:

    Foo +1, Bar +2*, Knowledge (arcana, history) -8

... etc.

"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers
## appease pyflakes
numbers


grammar = ( # {{{
r'''# skill stat
<n> := digit+
<ws> := [ \t]*
<nameChar> := [0-9a-zA-Z'" \t]
<name> := nameChar+

empty := '-'
splat := '*'

<subSkillName> := name
subSkillGroup := '(', !, subSkillName, (',', subSkillName)*, ')'

<qualifierChar> := [-+0-9a-zA-Z'" \t,]
qualifier := '(', !, qualifierChar+, ')'

value := [-+], !, ws, n

baseSkillName := name 
>skill< := baseSkillName, ws, !, subSkillGroup?, ws, value, ws, splat?, ws, qualifier?, ws, splat?

languageStart := 'Speak Language'
>language< := languageStart, !, ws, subSkillGroup?

>skillSlot< := language/skill
>skillList< := skillSlot, (',', ws, !, skillSlot)*
skillStat := empty/skillList
skillStatRoot := skillStat
''') # }}}


skillParser = parser.Parser(grammar, root='skillStatRoot')


class Processor(disp.DispatchProcessor):
    def skillStat(self, (t,s1,s2,sub), buffer):
        self.skills = []
        disp.dispatchList(self, sub, buffer)
        return self.skills

    def empty(self, *a, **kw):
        pass

    def addSkill(self, name):
        si = SkillItem()
        self.currentSkill = si
        si.skillName = name
        self.skills.append(si)

    def languageStart(self, (t,s1,s2,sub), buffer):
        self.addSkill('Speak Language')
        disp.dispatchList(self, sub, buffer)

    def baseSkillName(self, (t,s1,s2,sub), buffer):
        self.addSkill(disp.getString((t,s1,s2,sub), buffer).strip())

    def subSkillGroup(self, (t,s1,s2,sub), buffer):
        self.currentSkill.subSkills = disp.getString((t,s1+1,s2-1,sub),
                buffer).strip()

    def splat(self, (t,s1,s2,sub), buffer):
        self.currentSkill.splat = '*'

    def qualifier(self, (t,s1,s2,sub), buffer):
        self.currentSkill.qualifier = disp.getString((t,s1+1,s2-1,sub),
            buffer).strip()

    def value(self, (t,s1,s2,sub), buffer):
        self.currentSkill.value = int(buffer[s1:s2])


def parseSkills(s):
    succ, children, end = skillParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid skill expression' % (s,))
    return children


class SkillItem(object):
    def __init__(self):
        self.skillName = self.splat = self.qualifier = self.value = None
        self.subSkills = None

    def __repr__(self):
        return '<%s>' % (str(self),)

    def __str__(self):
        sub = ''
        if self.subSkills is not None:
            sub = ' (%s)' % (self.subSkills,)

        qual = ''
        if self.qualifier is not None:
            qual = ' (%s)' % (self.qualifier,)

        splat = ''
        if self.splat is not None:
            splat = '*'

        if self.value:
            return "%s%s %+d%s%s" % (self.skillName, sub, self.value, splat, qual)
        else:
            return "%s%s%s%s" % (self.skillName, sub, splat, qual)


tests = ( # {{{
"""-
Speak Language (elven, common)
Speak Language (any five), Jump +16*
Concentration +19, Craft or Knowledge (any three) +19, Diplomacy +22, Escape Artist +19, Hide +19, Intimidate +20, Listen +23, Move Silently +19, Sense Motive +19, Spot +23, Use Rope +4 (+6 with bindings)
Concentration -6, Hide +7, Move Silently +5, Psicraft +7, Ride +5, Spot +3
Knowledge (psionics) +12, Speak Language (ninjish), Jump +1
Hide +15, Move Silently +7, Listen +6, Spot +2
Hide +1000, Listen +5, Spot +5
Hide +9, Intimidate +12, Knowledge (psionics) +12, Listen +14, Psicraft +12, Search +12, Sense Motive +12, Spot +14* (comma, comma, ninjas)
Concentration +17, Hide +7, Jump +16, Knowledge (arcana) +12, Knowledge (psionics) +12, Knowledge (the planes) +12, Listen +22, Move Silently +11, Psicraft +12, Search +12, Sense Motive +14, Spot +22
Concentration +14, Diplomacy +17, Jump +0, Knowledge (any two) +15, Listen +16, Search +15, Sense Motive +16, Spellcraft +15 (+17 scrolls), Spot +16, Survival +4 (+6 following tracks), Tumble +15, Use Magic Device +15 (+17 scrolls)
Appraise +9, Climb +5, Jump +5, Listen +2, Spot +10
Climb +3, Jump +3
Listen +6, Move Silently +4, Spot +6
Spot +1
Bluff + 15, Concentration +11 (+15 when manifesting defensively), Hide +14, Listen +14, Move Silently +16
Jump +16 (or as controlling spirit)
Climb +38, Knowledge (psionics, arcane) +31, Listen +30, Psicraft +31, Spot +30
Climb +38 (+39 on a good day)*
Listen +11, Move Silently +7, Spot +11
Climb +14*, Listen +6, Move Silently +6, Search +2, Spot +6
Hide +22, Listen +7, Sense Motive +7, Spot +7
Climb +12, Jump +20, Listen +7, Spot +8
Listen +10
Bluff +10*, Diplomacy +6, Disguise +10*, Intimidate +6, Listen +6, Sense Motive +6, Spot +6
Climb and Skip +2, Jump +2
""".splitlines()) # }}}

if __name__ == '__main__':
    for t in tests:
        print t
        parsed = parseSkills(t)
        print parsed
