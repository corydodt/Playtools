
from zope.interface import Interface, Attribute

class ICharSheetSection(Interface):
    def asText(graph):
        pass


class IRuleSystem(Interface):
    """
    A rule system, such as D&D or Pathfinder.

    This may provide some insight: http://wiki.goonmill.org/PlaytoolsCompatibleGameSystems
    """
    facts = Attribute("facts")
    version = Attribute("version")
    __doc__ = Attribute("__doc__") # part of the interface because we use it
    name = Attribute("name")
    searchIndexPath = Attribute("searchIndexPath")


class IRuleCollection(Interface):
    """
    A RuleCollection provides an interface to the collection of RuleFacts that
    have the same type.
    """
    systems = Attribute("systems")
    factName = Attribute("factName")

    def __getitem__(self, key):
        """
        Synonym for lookup
        """

    def lookup(idOrName):
        """
        Get a single IRuleFact that is uniquely identified by idOrName
        """

    def dump():
        """
        All the RuleFacts this collection can find
        """


class IRuleFact(Interface):
    """
    One instance from a collection of rules
    """
    collection = Attribute("collection")  # set to the collection that corresponds to me


class IIndexable(Interface):
    uri = Attribute("uri")
    title = Attribute("title")
    text = Attribute("text")


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


class IPublisher(Interface):
    name = Attribute("name")
    def format(**kwargs):
        """
        Stringify the object I was initialized with.  Optional kwargs specify
        parameters that can be passed in to modify the formatting.
        """
