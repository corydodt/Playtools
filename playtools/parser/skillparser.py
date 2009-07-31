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

subSkillName := name
>subSkillGroup< := '(', !, subSkillName, (',', subSkillName)*, ')'

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

    def subSkillName(self, (t,s1,s2,sub), buffer):
        self.currentSkill.subSkills.append(disp.getString((t,s1,s2,sub),
            buffer).strip())

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
        self.subSkills = []

    def __repr__(self):
        return '<%s>' % (str(self),)

    def __str__(self):
        sub = ''
        if self.subSkills:
            sub = ' (%s)' % (', '.join(self.subSkills),)

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

