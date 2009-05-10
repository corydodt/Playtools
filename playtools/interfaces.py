
from zope.interface import Interface, Attribute

class ICharSheetSection(Interface):
    def asText(graph):
        pass


class IRuleFact(Interface):
    """
    A RuleFact is a certain kind of searchable, formattable object such as a
    Monster, Spell, Skill, Feat, Equipment, etc.  The domain of these things
    is an interface that allows use to index, look up, search for, and
    pretty-format them.
    """
    def indexableText():
        """
        The full text of the fact, in a format that can be indexed by a
        fulltext indexer.
        """


class IFormatter(Interface):
    """
    Make an IRuleFact into a human-readable text
    """
    formatName = Attribute('formatName')

    def format():
        """
        Convert the fact into a piece of text
        """


class IConverter(Interface):
    """
    A converter takes data from an abritrary source (plugin-implemented) and
    writes an entry in Playtools format.
    """
    commandLine = Attribute("commandLine")

    def next():
        """
        Retrieve one unit from the data source and return it
        """

    def makePlaytoolsItem(item):
        """
        Add triples for this item to the db
        """

    def writeAll(playtoolsIO):
        """
        Format the document as N3/RDF and write it to the playtoolsIO object
        """

    def label():
        """
        Identify this converter with a string
        """

    def __iter__():
        """
        IConverters are iterators
        """

    def preamble():
        """
        Add any header triples
        """


