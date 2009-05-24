"""
Utilities for creating simple publisher plugins
"""
from zope.interface import implements 

from twisted.plugin import IPlugin

class PublisherPlugin(object):
    """
    Base class (convenience class) for objects that want to be publishers of a
    single collection only.
    """
    implements(IPlugin)
    collection = None
    def __init__(self, systemName, collectionName):
        self.systemName = systemName
        self.collectionName = collectionName


