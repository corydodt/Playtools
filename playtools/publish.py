"""
Base system for creating formatter implementations
"""

from playtools.interfaces import IPublisher, IRuleCollection

_publisherRegistry = {}

def addPublisher(collection, publishClass):
    """
    Use klass to publish objects in the collection of fact
    """
    assert IPublisher.implementedBy(publishClass)
    assert IRuleCollection.providedBy(collection)
    _publisherRegistry[(collection, publishClass.name)] = publishClass

def publish(fact, format, **kw):
    """
    Convert fact into format and return a string.  Known keywords may be used
    to modify formatting, specific to each formatter.
    """
    return Publisher(fact, format).format(**kw)


class Publisher(object):
    """
    Take an IRuleFact provider and provide access to the known formatters for
    that format.
    """
    def __init__(self, fact, format):
        self.fact = fact
        self.outputFormat = format

    def format(self, **kw):
        klass = _publisherRegistry[(self.fact.collection, self.outputFormat)]
        formatter = klass()
        return formatter.format(self.fact, **kw)

