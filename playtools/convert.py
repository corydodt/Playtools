try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

from zope.interface import Interface, Attribute, implements
from twisted.plugin import getPlugins


XHTML_NS = 'http://www.w3.org/1999/xhtml#'

class IPlaytoolsIO(Interface):
    """
    IO-handling interface.  It may be used to write either XML or N3.
    """
    def writeXml(s):
        """
        Call to write XML data
        """

    def writeN3(s):
        """
        Call to write n3 data
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

    def makePlaytoolsItem(playtoolsIO, item):
        """
        Add triples for this item to the db
        """

    def writeAll():
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

    def preamble(playtoolsIO):
        """
        Write any header info to playtoolsIO
        """


class PlaytoolsIO(object):
    implements(IPlaytoolsIO)
    def __init__(self, n3file, xmlfile):
        self.n3file = n3file
        self.xmlfile = xmlfile

    def writeN3(self, s):
        self.n3file.write(s)

    def writeXml(self, s):
        self.xmlfile.write(s)


def getConverters():
    import playtools.plugins
    l = list(getPlugins(IConverter, playtools.plugins))
    return l

def getConverter(converterName):
    for c in getConverters():
        if c.label() == converterName:
            return c
    raise KeyError("Converter %s not found" % (converterName,))

def rdfXmlWrap(s, about, predicate, contentsNamespace=XHTML_NS):
    """Return an rdf:Description of s.
    contentsNamespace is xmlns for all the nodes parsed from s
    about is the about URI for the rdf:Description
    predicate is a 2-tuple of tagName and namespace for the inner tag
    """
    desc = ElementTree.Element("Description", 
            xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            about=about,
            parseType="Literal"
    )
    tag, predicateNamespace = predicate
    inner = u"<%s>%s</%s>" % (tag, s, tag)
    try:
        parsed = ElementTree.fromstring(inner)
    except:
        import sys, pdb; pdb.post_mortem(sys.exc_info()[2])

    parsed.set('xmlns', predicateNamespace)
    for e in parsed.getchildren():
        e.set('xmlns', contentsNamespace)

    desc.append(parsed)

    # TODO - make prefixes nicer
    return ElementTree.tostring(desc)

def rdfName(s):
    """Return a string suitable for an IRI from s"""
    s = s.replace('.', ' ')
    s = s.replace('-', ' ')
    s = s.replace("'", '')
    s = s.replace('/', ' ')
    s = s.replace(':', ' ')
    s = s.replace(',', ' ')
    s = s.replace('(', ' ').replace(")", ' ')
    s = s.replace('[', ' ').replace("]", ' ')
    parts = s.split()
    parts[0] = parts[0].lower()
    parts[1:] = [p.capitalize() for p in parts[1:]]
    return ''.join(parts)

def converterDoc(converter):
    if converter.__doc__ is None:
        return ''
    return converter.__doc__.splitlines()[0].rstrip()

__all__ = ['IPlaytoolsIO', 'IConverter', 'PlaytoolsIO', 'getConverters',
        'getConverter', 'rdfXmlWrap', 'rdfName']

