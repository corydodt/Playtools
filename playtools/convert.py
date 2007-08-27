from zope.interface import Interface
from twisted.plugin import getPlugins


class IConverter(Interface):
    """
    A converter takes data from an abritrary source (plugin-implemented) and
    writes an entry in Playtools format.
    """
    def getNextItem():
        """
        Retrieve one unit from the data source and return it
        """

    def writePlaytoolsItem(playtoolsIO):
        """
        Format the current item as N3/RDF and write it to the playtoolsIO
        object
        """

def getConverters():
    import playtools.plugins
    return list(getPlugins(IConverter, playtools.plugins))

print getConverters()
