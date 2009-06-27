"""
Some predefined app-specific namespaces and other junk we use a lot.
"""

from rdflib.Namespace import Namespace as NS
from rdflib.RDFS import RDFSNS
from rdflib.RDF import RDFNS
from rdflib import URIRef

skillNs = NS("http://goonmill.org/2007/skill.n3#")
featNs = NS("http://goonmill.org/2007/feat.n3#")
monsterNs = NS("http://goonmill.org/2007/monster.n3#")
P = NS('http://goonmill.org/2007/property.n3#')
C = NS('http://goonmill.org/2007/characteristic.n3#')

a = RDFNS.type

this = URIRef('')

# for pyflakes
RDFSNS
RDFNS
