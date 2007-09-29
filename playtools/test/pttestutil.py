"""
Utilities for unit tests
"""
from itertools import chain, repeat
try:
    from xml.etree import cElementTree as ET
    ET # for pyflakes
except ImportError:
    from xml.etree import ElementTree as ET

from rdflib.Graph import Graph
from rdflib import BNode

def padSeq(seq, padding):
    return chain(seq, repeat(padding))


def padZip(l1, l2, padding=None):
    """
    Return zip(l1, l2), but the shorter sequence will be padded to the length
    of the longer sequence by the padding
    """
    if len(l1) > len(l2):
        return zip(l1, padSeq(l2, padding))
    elif len(l1) < len(l2):
        return zip(padSeq(l1, padding), l2)

    return zip(l1, l2)


def formatFailMsg(seq, left="|| "):
    """Display the sequence of lines, with failure message"""
    ret = ['%r != %r\n']
    for s in seq:
        ret.append("%s%s\n" % (left, s))
    return ''.join(ret)


def compareElement(e1, e2):
    """Return None if they are identical, otherwise return the elements that differed"""
    if e1 is None or e2 is None:
        return e1, e2

    # compare attributes
    it1 = sorted(e1.items())
    it2 = sorted(e2.items())
    if it1 != it2:
        return e1, e2

    # compare text
    if e1.text != e2.text:
        return e1, e2

    # compare tail'd text
    if e1.tail != e2.tail:
        return e1, e2

    ch1 = e1.getchildren()
    ch2 = e2.getchildren()
    for c1, c2 in padZip(ch1, ch2):
        comparison = compareElement(c1, c2)
        if not comparison is None:
            return comparison

    return None


def compareXml(s1, s2):
    """
    Parse xml strings s1 and s2 and compare them
    """
    x1 = ET.fromstring(s1)
    x2 = ET.fromstring(s2)

    compared = compareElement(x1, x2)
    if compared is None:
        return True

    # TODO - return some information about the parts of the xml that differed
    return False


class IsomorphicTestableGraph(Graph):
    """
    Taken from http://www.w3.org/2001/sw/grddl

    Modified to ALSO test prefix identicality.
    """
    def __init__(self, **kargs): 
        super(IsomorphicTestableGraph,self).__init__(**kargs)
        self.hash = None
        
    def internal_hash(self):
        """
        This is defined instead of __hash__ to avoid a circular recursion scenario with the Memory
        store for rdflib which requires a hash lookup in order to return a generator of triples
        """ 
        return hash(tuple(sorted(self.hashtriples())))

    def hashtriples(self): 
        for triple in self: 
            g = ((isinstance(t,BNode) and self.vhash(t)) or t for t in triple)
            yield hash(tuple(g))

    def vhash(self, term, done=False): 
        return tuple(sorted(self.vhashtriples(term, done)))

    def vhashtriples(self, term, done): 
        for t in self: 
            if term in t: yield tuple(self.vhashtriple(t, term, done))

    def vhashtriple(self, triple, term, done): 
        for p in xrange(3): 
            if not isinstance(triple[p], BNode): yield triple[p]
            elif done or (triple[p] == term): yield p
            else: yield self.vhash(triple[p], done=True)
      
    def __eq__(self, G): 
        """Graph isomorphism testing."""
        if not isinstance(G, IsomorphicTestableGraph): 
            return False
        elif len(self) != len(G): 
            return False
        # check namespaces are bound to the same prefixes!
        elif sorted(self.namespaces()) != sorted(G.namespaces()): 
            return False
        elif list.__eq__(list(self),list(G)): 
            return True # @@
        return self.internal_hash() == G.internal_hash()

    def __ne__(self, G): 
       """Negative graph isomorphism testing."""
       return not self.__eq__(G)
