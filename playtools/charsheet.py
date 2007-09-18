
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
charsheet = NS('http://thesoftworld.com/2007/charsheet.n3#')

def getCharSheetSections():
    import playtools.plugins
    l = getPlugins(ICharSheetSection, playtools.plugins)
    return dict((s.__class__.__name__, s) for s in l)

def showCharSheet(section, graph, ns):
    try:
        section.asText(graph, ns)
    except KeyError, e:
        import traceback
        traceback.print_exc()
        print 'Not printing', section, 'because', e

def main(filename, name):
    all_sections = getCharSheetSections()

    charactersheet = NS('http://trinket.thorne.id.au/2007/%s.n3#' % name)
    character = URIRef(charactersheet + name)

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

    
    for (sections,) in graph.query(
            "SELECT ?sections { ?character charsheet:sections ?sections }", 
                {'?character':character}, 
                initNs={'charsheet':charsheet}):
        for item in graph.items(sections):
            showCharSheet(all_sections[item], graph, character)


