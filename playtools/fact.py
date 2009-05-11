"""
Access to facts given by the game systems we know about.
"""

from .interfaces import IRuleSystem, IRuleCollection
from . import plugins

from twisted.plugin import getPlugins

def getSystems():
    """
    Doubly-indexed dict of the game systems we have been able to find through
    the plugin system.  Find by either systems[name] or systems[(name, version)]
    """
    l = list(getPlugins(IRuleSystem, plugins))
    ret = {}
    for system in l:
        ret[(system.name, system.version)] = system
        # FIXME - ambiguously clobber ret[system.name] sometimes.
        ret[system.name] = system
    return ret

systems = getSystems()

def importRuleCollections():
    """
    Search for IRuleCollection classes with the plugin system and associate
    them with the systems in the systems dict
    """
    l = list(getPlugins(IRuleCollection, plugins))
    for collection in l:
        for s in collection.systems:
            systems[s.name].facts[collection.factName] = collection

importRuleCollections()

all = ['systems']
