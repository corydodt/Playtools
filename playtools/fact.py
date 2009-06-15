"""
Access to facts given by the game systems we know about.
"""

from .interfaces import IRuleSystem, IRuleCollection
from playtools import PLUGINMODULE

from twisted.plugin import getPlugins


class SystemLoader(object):
    """
    Dictionary-like that defers plugin loading until the first time someone wants a
    plugin (by using systems[name] syntax, i.e. invoking __getitem__).

    This provides rudimentary protection against circular imports.

    Doubly-indexed dict of the game systems we have been able to find through
    the plugin system.  Find by either systems[name] or systems[(name, version)]
    """
    _cachedPlugins = None

    def __getitem__(self, name):
        if self._cachedPlugins is None:
            self._cachedPlugins = getSystems()
            importRuleCollections(self._cachedPlugins)

        return self._cachedPlugins[name]

    def __contains__(self, name):
        return name in self._cachedPlugins


def getSystems():
    l = list(getPlugins(IRuleSystem, PLUGINMODULE))
    ret = {}
    for system in l:
        ret[(system.name, system.version)] = system
        # FIXME - ambiguously clobber _cachedPlugins[system.name] sometimes.
        ret[system.name] = system

    return ret

def importRuleCollections(gameSystems):
    """
    Search for IRuleCollection classes with the plugin system and associate
    them with the systems in the systems dict
    """
    l = list(getPlugins(IRuleCollection, PLUGINMODULE))
    for collection in l:
        gameSystems[collection.system.name].facts[collection.factName] = collection

systems = SystemLoader()

all = ['systems']
