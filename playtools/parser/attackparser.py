from . import diceparser
diceparser

from simpleparse import parser, dispatchprocessor as disp, objectgenerator
from simpleparse import common
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

grammar = ( # {{{
r'''# Attacks!
<wsc>                     :=  [ \t]
<ws>                      :=  wsc*
<n>                       :=  int
<l>                       :=  letter
<d>                       :=  digit
<paren>                   :=  [()]
<splat>                   :=  '*'

count                     :=  n

<weaponChar>              :=  l/d/wsc/paren
<nonTerminalDash>         :=  ('-', l)
weapon                    :=  (weaponChar/nonTerminalDash)+

bonus                     :=  [-+], n
bonusSequence             :=  bonus, ('/', bonus)*

>cwb<                     :=  count?, ws, weapon, ws, bonusSequence

attackTypeSlot            :=  ('melee'/'ranged'), splat?
attackTouchSlot           :=  'touch'
>attackTypeAndTouch<      :=  attackTypeSlot, ws, attackTouchSlot?

<critRange>               :=  n, '-', n
<critThreat>              :=  'x', !, n
crit                      :=  (critRange, '/', critThreat)/critRange/critThreat
>critPhrase<              :=  '/', !, crit  

extraDamage1              :=  'plus'/'+', !, ws, (l/d/[,+-])+, (ws, (l/d/[,+-])+)*
>extraDamage2<            :=  '(', !, extraDamage1, ')'
>extraClause<             :=  (extraDamage2/extraDamage1)+

damageType                :=  (l/d)+, (ws, (l/d/'+')+)*
<_diceExpression>         :=  diceExpression

damageWithType            :=  _diceExpression, (ws, splat)?, ws, damageType
damageWithoutType         :=  _diceExpression, (ws, splat)?

>diceOnly<                :=  damageWithoutType, critPhrase?
>nonDiceDamage<           :=  damageType, critPhrase?
>diceAndTypeDamage<       :=  damageWithType, critPhrase?
>diceAndExtraDamage<      :=  damageWithoutType, critPhrase?, ws, extraClause
>diceTypeAndExtraDamage<  :=  damageWithType, critPhrase?, ws, extraClause

>damage<                  :=  diceTypeAndExtraDamage/diceAndExtraDamage/diceAndTypeDamage/diceOnly/nonDiceDamage

>damagePhrase<            :=  '(', !, damage, ws, ')'

<rangeInformation>        :=  (l/d/[.+-])+, (ws, (l/d/[.+-])+)*
rangeSlot                 :=  '(', !, rangeInformation, ')'

# two choices
>subAttackForm1<          :=  damagePhrase, ws, attackTypeAndTouch
>subAttackForm2<          :=  attackTypeAndTouch, ws, damagePhrase

anyAttackForm             :=  cwb, ws, !, subAttackForm1/subAttackForm2, ws, rangeSlot?

<attackFormSep>           :=  ','/'and'

attackGroup               :=  anyAttackForm, (attackFormSep, ws, anyAttackForm)*

empty                     :=  '-'

attackStat                :=  empty/(attackGroup, (';'?, ws, 'or', ws, attackGroup)*)

attackStatRoot            :=  attackStat
''') # }}}

attackParser = parser.Parser(grammar, root='attackStatRoot')


class AttackGroup(object):
    """A group of AttackForms which all may be used simultaneously"""
    def __init__(self):
        self.attackForms = []

    def __repr__(self):
        return '<AttackGroup with %s forms>' % (len(self.attackForms),)


class AttackForm(object):
    """A series of attacks with the same weapon"""
    def __init__(self):
        self.extraDamage = []
        self.crit = '20'
        self.count = 1
        self.touch = ''
        self.type = None
        self.damage = None
        self.rangeInformation = ''
        self.bonus = ()
        self.weapon = ''

    def __repr__(self):
        return '<AttackForm %s|%s|%s|%s|%s|%s|%s|%s|%s>' % (self.count, 
                self.weapon, 
                ['%+d'%(b,) for b in self.bonus], 
                self.damage, 
                self.crit, self.extraDamage, self.type,
                self.touch,
                self.rangeInformation)

    def __str__(self):
        # do minimizations
        count = ''
        if self.count > 1:
            count = '%s ' % (self.count,)

        weapon = self.weapon

        bonus = '/'.join(['%+d'%(b,) for b in self.bonus])

        damage = self.damage

        crit = ''
        if self.crit != '20':
            crit = '/%s' % (self.crit,)

        extra = ''
        for ed in self.extraDamage:
            extra = extra + ' (%s)' % (ed,)

        type = self.type

        touch = ''
        if self.touch:
            touch = ' %s' % (self.touch,)

        range = ''
        if self.rangeInformation:
            range = ' (%s)' % (self.rangeInformation,)

        return '%s%s %s (%s%s%s) %s%s%s' % (
                count, weapon, bonus, damage, crit, extra, type, touch, range)


class Processor(disp.DispatchProcessor):
    def __init__(self, attackGroups=None, *a, **kw):
        if attackGroups is not None:
            self.attackGroups = attackGroups
            self.option = self.attackGroups[-1]
            self.attackForm = self.option.attackForms[-1]
        else:
            self.attackGroups = []
        ## no such thing: disp.DispatchProcessor.__init__(self, *a, **kw)

    def attackStat(self, (t,s1,s2,sub), buffer):
        disp.dispatchList(self, sub, buffer)
        return self.attackGroups

    def empty(self, (t,s1,s2,sub), buffer):
        pass

    def count(self, (t,s1,s2,sub), buffer):
        self.attackForm.count = int(buffer[s1:s2])

    def bonusSequence(self, (t,s1,s2,sub), buffer):
        s = disp.getString((t,s1,s2,sub), buffer)
        bonuses = []
        for bonus in s.split('/'):
            bonuses.append(int(bonus))
        self.attackForm.bonus = bonuses

    def weapon(self, (t,s1,s2,sub), buffer):
        self.attackForm.weapon = disp.getString((t,s1,s2,sub), buffer).strip()

    def rangeSlot(self, (t,s1,s2,sub), buffer):
        self.attackForm.rangeInformation = disp.getString((t,s1+1,s2-1,sub), buffer)

    def damageWithType(self, (t,s1,s2,sub), buffer):
        self.attackForm.damage = disp.getString((t,s1,s2,sub), buffer)

    def damageWithoutType(self, (t,s1,s2,sub), buffer):
        self.attackForm.damage = disp.getString((t,s1,s2,sub), buffer).strip()

    def damageType(self, (t,s1,s2,sub), buffer):
        self.attackForm.damage = disp.getString((t,s1,s2,sub), buffer)

    def extraDamage1(self, (t,s1,s2,sub), buffer):
        ed = disp.getString((t,s1,s2,sub), buffer).strip()
        self.attackForm.extraDamage.append(ed)

    def crit(self, (t,s1,s2,sub), buffer):
        self.attackForm.crit = disp.getString((t,s1,s2,sub), buffer)

    def attackTypeSlot(self, (t,s1,s2,sub), buffer):
        self.attackForm.type = disp.getString((t,s1,s2,sub), buffer)

    def anyAttackForm(self, (t,s1,s2,sub), buffer):
        form = AttackForm()
        self.option.attackForms.append(form)
        self.attackForm = form
        return disp.dispatchList(self, sub, buffer)

    def attackGroup(self, (t,s1,s2,sub), buffer):
        self.option = AttackGroup()
        self.attackGroups.append(self.option)
        return disp.dispatchList(self, sub, buffer)

    def attackTouchSlot(self, (t,s1,s2,sub), buffer):
        self.attackForm.touch = 'touch'

    def staticNumber(self, (t,s1,s2,sub), buffer):
        self.expr.staticNumber = int(buffer[s1:s2])


def parseAttacks(s, production=None, probe=None):
    if production is None:
        extraArgs = {}
    else:
        extraArgs = {'production':production}
    proc = Processor(probe)
    succ, children, end = attackParser.parse(s, processor=proc, **extraArgs)
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid attack expression' % (s,))
    return children

# make productions exportable
c = {}
for name in ['extraDamage1']:
	c[ name ] = objectgenerator.LibraryElement(
		generator = attackParser._generator,
		production = name,
	)

common.share( c )
