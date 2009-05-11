"""
The Pathfinder RPG
"""
from zope.interface import implements
from twisted.plugin import IPlugin
from playtools.interfaces import IRuleSystem

class PathfinderSystem(object):
    """
    Paizo's Pathfinder role-playing game system.  See 
    http://paizo.com/pathfinder/
    """
    implements (IRuleSystem, IPlugin)
    name = "Pathfinder"
    version = "1.0"


pathfinder10 = PathfinderSystem()
pathfinder10.facts = {}
