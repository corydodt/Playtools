"""
Implement dice rolling using parsed dice
"""
import sys
import random

from playtools.parser import diceparser

def rollDie(die, mod=0):
    return random.choice(range(1, die+1)) + mod

def parseRange(odds):
    """parseRange("2-15") => (2, 15) (as ints)
    Also parseRange("2") => (2, 2)
    """
    if '-' in odds:
        low,hi = odds.split('-')
    else:
        low = hi = odds
    return int(low), int(hi)

def choosePercentile(percentiles):
    """Utility function for choosing an item from a list formatted like this:
    ['01-11','12-73','74-99','100']
    Returns the index of the item selected from the list.
    """
    pctile = roll(100)
    for n, outcome in enumerate(percentiles):
        low,hi = parseRange(outcome)
        if low <= pctile <= hi:
            return n
    raise RuntimeError, "None of %s were selected" % (percentiles,)


def parse(st):
    """The results of rolling this dice expression, as a list of sums"""
    parsed = diceparser.parseDice(st)
    rolled = roll(parsed)
    return list(rolled)

def roll(parsed, temp_modifier=0):
    # set these to defaults in the finish step, not in the init, 
    # so the parser instance can be reused
    count = parsed.count
    if parsed.filterCount is not None:
        dice_filter_count = parsed.filterCount
        if dice_filter_count > count:
            _m = "Hi/Lo filter uses more dice than are being rolled"
            raise RuntimeError(_m)

        hilo = str(parsed.filterDirection)
    else:
        dice_filter_count = 0
        hilo = None

    dice_repeat = parsed.repeat

    dice_bonus = parsed.dieModifier

    if parsed.staticNumber is not None:
        # an int by itself is just an int.
        for n in xrange(dice_repeat):
            yield DiceResult([parsed.staticNumber], dice_bonus, temp_modifier)
        return

    for n in xrange(dice_repeat):
        dierolls = []
        for n in xrange(count):
            dierolls.append(rollDie(parsed.dieSize, 0))
        result = DiceResult(dierolls, 
                            dice_bonus, 
                            temp_modifier,
                            hilo, 
                            dice_filter_count)
        yield result

class DiceResult:
    """Representation of all the values rolled by a dice expression."""
    def __init__(self, dierolls, bonus, temp_modifier=0, filterdirection=None, 
                 filtercount=0):
        self.dierolls = dierolls
        self.bonus = bonus
        if temp_modifier:
            self.temp_modifier = temp_modifier
        else:
            self.temp_modifier = 0
           
        self.filterdirection = filterdirection
        self.filtercount = filtercount

    def __repr__(self):
        return 'DiceResult(=%s)' % self.sum()

    def format(self):
        """Print the sum of the individual (filtered) dice and bonus"""
        dierolls = self.filtered()[:]
        if self.bonus:
            dierolls.append(self.bonus)
        if self.temp_modifier:
            dierolls.append(self.temp_modifier)

        if len(dierolls) > 1:
            formatted_sum = '+'.join(map(str, dierolls))
            return '%s = %s' % (formatted_sum, self.sum())
        else:
            return str(self.sum())

    def filtered(self):
        if self.filterdirection is None:
            filter = lambda: self.dierolls
        elif self.filterdirection in 'hH':
            filter = self.most
        elif self.filterdirection in 'lL':
            filter = self.least
        return filter()

    def sum(self):
        return sum(self.filtered()) + self.bonus + self.temp_modifier

    def __cmp__(self, other):
        return cmp(self.sum(), other.sum())

    def most(self, direction=1):
        """Return the greatest <count> items in lst"""
        lst = self.dierolls[:]
        lst.sort()
        if direction == 1:
            lst.reverse()
        return lst[:self.filtercount]

    def least(self):
        return self.most(0)


def run(argv=None):
    if argv is None:
        argv = sys.argv
    while 1:
        try:
            st = raw_input("Roll: ")
            rolled = [r.sum() for r in parse(st)]
            if len(list(rolled)) > 1:
                print "Unsorted--", rolled
                rolled.sort()
                rolled.reverse()
                print "Sorted----", rolled
            else:
                print rolled
        except RuntimeError, e:
            print e

