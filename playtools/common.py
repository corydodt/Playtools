"""
Some predefined app-specific namespaces and other junk we use a lot.
"""

from rdflib.Namespace import Namespace as NS
from rdflib.RDFS import RDFSNS
from rdflib import URIRef

skillNs = NS("http://thesoftworld.com/2007/skill.n3#")
P = NS('http://thesoftworld.com/2007/properties.n3#')
C = NS('http://thesoftworld.com/2007/chracteristic.n3#')

a = RDFSNS.typeof

this = URIRef('')
