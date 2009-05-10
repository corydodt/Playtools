try:
    from xml.etree import cElementTree as ElementTree
    ElementTree # for pyflakes
except ImportError:
    from xml.etree import ElementTree

from twisted.plugin import getPlugins
from .interfaces import IConverter


XHTML_NS = 'http://www.w3.org/1999/xhtml#'


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

def converterDoc(converter):
    if converter.__doc__ is None:
        return ''
    return converter.__doc__.splitlines()[0].rstrip()

__all__ = ['getConverters', 'getConverter', 'rdfXmlWrap']

