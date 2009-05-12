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


class FakeFactCollection(object):
    """
    A pretend collection of RuleFacts
    """
    implements(IRuleCollection, IPlugin)
    systems = (BuildingsAndBadgersSystem,)

    def __init__(self, factName):
        self.factName = factName

    def __getitem__(self, key):
        raise NotImplemented()

    def dump(self):
        """
        All instances of the factClass
        """
        raise NotImplemented()

    def lookup(self, idOrName):
        raise NotImplemented()

buildings = FakeFactCollection('buildings')
badgers = FakeFactCollection('badgers')
