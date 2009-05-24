"""
Base system for creating formatter implementations
"""
from zope.interface import implements

from twisted.plugin import IPlugin, getPlugins

from playtools.interfaces import IPublisher, IRuleCollection
import playtools.plugins

PLUGINMODULE = playtools.plugins  # making it possible to monkey-patch this in test code

def publish(fact, format, **kw):
    """
    Convert fact into format and return a string.  Known keywords may be used
    to modify formatting, specific to each formatter.
    """
    return Publisher(fact, format).format(**kw)

def getPublishers():
    """
    Index of the publishers we have been able to find through the plugin
    system.
    """
    l = list(getPlugins(IPublisher, PLUGINMODULE))
    ret = {}
    for pub in l:
        ret[(pub.collection, pub.name)] = pub
    return ret

publishers = getPublishers()

def override(collection, publisher):
    """
    Install a new publisher over whatever publisher is currently available for
    the particular format and collection being published.
    """
    assert IPublisher.providedBy(publisher)
    assert IRuleCollection.providedBy(collection)
    publishers[(collection, publisher.name)] = publisher


class PublisherPlugin(object):
    """
    Base class (convenience class) for objects that want to be publishers of a
    single collection only.
    """
    implements(IPlugin)
    collection = None
    def __init__(self, collection):
        assert IRuleCollection.providedBy(collection)
        self.collection = collection


class Publisher(object):
    """
    Take an IRuleFact provider and provide access to the known formatters for
    that format.
    """
    def __init__(self, fact, format):
        self.fact = fact
        self.outputFormat = format

    def format(self, **kw):
        formatter = publishers[(self.fact.collection, self.outputFormat)]
        return formatter.format(self.fact, **kw)

