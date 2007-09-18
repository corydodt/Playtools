
from rdflib import ConjunctiveGraph
from rdflib.Namespace import Namespace as NS
from playtools import sparqly
import glob
from twisted.python.util import sibpath
import os
from rdflib import URIRef

from twisted.plugin import getPlugins, IPlugin
from zope.interface import Interface, Attribute, implements
from playtools.interfaces import ICharSheetSection

rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')
rdf = NS("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

def getCharSheetSections():
    import playtools.plugins
    l = list(getPlugins(ICharSheetSection, playtools.plugins))
    return l

def showCharSheet(sections, graph, ns):
    for section in sections:
        try:
            section.asText(graph, ns)
        except KeyError, e:
            import traceback
            traceback.print_exc()
            print 'Not printing', section, 'because', e

def main(filename, name):
    sections = getCharSheetSections()

    charactersheet = NS('http://trinket.thorne.id.au/2007/%s.n3#' % name)
    player = URIRef(charactersheet + name)

    graph = ConjunctiveGraph()
    for f in glob.glob(os.path.join(sibpath(__file__, 'data'), '*.n3')):
        if f.endswith('monster.n3'):
            continue
        try: graph.load(f, format='n3')
        except Exception, e:
            import traceback
            print 'Could not load', f, 'because', e
    graph.load(rdfs)
    graph.load(rdf)

    graph.load(filename, format='n3')
    
    showCharSheet(sections, graph, player)


