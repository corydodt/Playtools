"""
A fake game system for testing game system plugins.
"""
from zope.interface import implements

from twisted.plugin import IPlugin

from playtools.interfaces import IRuleSystem, IRuleFact, IRuleCollection

class BuildingsAndBadgersSystem(object):
    """
    The Buildings & Badgers role-playing game
    """
    implements (IRuleSystem, IPlugin)
    name = "Buildings & Badgers"
    version = "2.06"
    searchIndexPath = "test/badgers-index"
    def __init__(self):
        self.facts = {}


buildingsAndBadgers = BuildingsAndBadgersSystem()


class Building(object):
    def __init__(self, id, name, text):
        self.id = id
        self.name = name
        self.full_text = text


class Badger(object):
    def __init__(self, id, name, text):
        self.id = id
        self.name = name
        self.full_text = text


database = {
'badger': [
    Badger(u'1', u'Small Badger', 'Small, pretty badger.'),
    Badger(u'73', u'Giant Man-Eating Badger', 'Giant, hideous, bad-tempered space badger.')
    ],

'building': [
    Building(u'2', u'Castle', 'A castle (where badgers live)'),
    Building(u'4', u'Dungeon', 'A dungeon (built by badgers)'),
    ],
}


class FakeFactCollection(object):
    """
    A pretend collection of RuleFacts
    """
    implements(IRuleCollection, IPlugin)
    systems = (BuildingsAndBadgersSystem,)

    def __init__(self, factName):
        self.factName = factName

    def __getitem__(self, key):
        ret = self.lookup(key)
        if ret is None:
            raise KeyError(key)
        return ret

    def dump(self):
        """
        All instances of the factClass
        """
        return database[self.factName][:]

    def lookup(self, k):
        items = database[self.factName]
        for item in items:
            if item.id == k or item.name == k:
                return item

buildings = FakeFactCollection('building')
badgers = FakeFactCollection('badger')
