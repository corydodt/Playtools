"""
A fake game system for testing game system plugins.
"""
import re
import string

from zope.interface import implements

from twisted.plugin import IPlugin

from playtools.interfaces import (IRuleSystem, IRuleFact, IRuleCollection,
        IIndexable,
        IPublisher)
from playtools import globalRegistry, publish

class BuildingsAndBadgersSystem(object):
    """
    The Buildings & Badgers role-playing game
    """
    implements (IRuleSystem, IPlugin)
    name = "Buildings & Badgers"
    version = "2.06"
    searchIndexPath = "test-badgers-index"
    def __init__(self):
        self.facts = {}


buildingsAndBadgers = BuildingsAndBadgersSystem()


class IBadgerFact(IRuleFact):
    """
    A test interface for badgery.
    """


class IndexableBadgerFact(object):
    """
    Trivial layer over facts that are objects in the badger database
    """
    implements(IIndexable)
    __used_for__ = IBadgerFact

    def __init__(self, fact):
        self.fact = fact
        self.text = fact.full_text
        self.uri = fact.id
        self.title = fact.name

globalRegistry.register([IBadgerFact], IIndexable, '', IndexableBadgerFact)


class Building(object):
    implements(IBadgerFact)
    def __init__(self, id, name, text, collection):
        self.id = id
        self.name = name
        self.full_text = text
        self.collection = collection


class Badger(object):
    implements(IBadgerFact)
    def __init__(self, id, name, text, collection):
        self.id = id
        self.name = name
        self.full_text = text
        self.collection = collection


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

class HTMLBuildingPublisher(object):
    implements(IPublisher)
    name = 'html'
    def format(self, building, title=None):
        t = string.Template(r"""<html><head>
<title>$title</title>
</head>
<body>
<h1>$title</h1>
$body
</body>
</html>
""")
        if title is None:
            title = building.name
        r = t.substitute(title=title, body=building.full_text)
        return r
        #

publish.addPublisher(buildings, HTMLBuildingPublisher)

database = {
'badger': [
    Badger(u'1', u'Small Badger', u'Small, pretty badger.', badgers),
    Badger(u'73', u'Giant Man-Eating Badger', u'Giant, hideous, bad-tempered space badger.', badgers)
    ],

'building': [
    Building(u'2', u'Castle', 'A castle (where badgers live)', buildings),
    Building(u'4', u'Dungeon', 'A dungeon (built by badgers)', buildings),
    ],
}
