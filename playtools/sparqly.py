"""
========
SPARQL-y
========

Utilities for using rdfalchemy with playtools
"""

import os.path
import hashlib
import random

try:
    from cStringIO import StringIO
    StringIO # for pyflakes
except ImportError:
    from StringIO import StringIO


from rdflib import URIRef, BNode, Literal
from rdflib.Graph import ConjunctiveGraph as Graph
from rdflib.Literal import Literal as RDFLiteral

from rdfalchemy.descriptors import rdfAbstract, rdfSingle
from rdfalchemy.rdfsSubject import rdfsClass

from playtools.common import RDFSNS, a as RDF_a


def select(base, rest):
    d = dict(base=base, rest=rest, )
    return """BASE <%(base)s> %(rest)s""" % d


def iriToTitle(iri):
    """Return the fragment id of the iri, in title-case"""
    if '#' not in iri:
        return ''
    uri = iri.lstrip('<').rstrip('>')
    ret = Literal(uri.split('#', 1)[1].title())
    return ret


NODEFAULT = ()


BAD_NAMESPACES = [
        'http://www.w3.org/XML/1998/namespace',
        'http://www.w3.org/2000/01/rdf-schema#',
        'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
]


def filterNamespaces(namespaces):
    """
    Remove namespaces that shouldn't really be loaded, such as XML
    """
    return [ns for ns in namespaces if str(ns) not in BAD_NAMESPACES]


def canBeLiteral(x):
    """
    True if x is a string, int or float
    """
    return (
            isinstance(x, basestring) or 
            isinstance(x, int) or
            isinstance(x, float)
            ) and not (
            hasattr(x, 'n3')
            )


class TriplesDatabase(object):
    """A database from the defined triples"""
    def __init__(self):
        self._open = False

    def open(self, filename, graphClass=None):
        """
        Load existing database at 'filename'.
        """
        if filename is None:
            if graphClass is None:
                self.graph = Graph()
            else:
                self.graph = graphClass()
        else:
            assert os.path.exists(filename), (
                    "%s must be an existing database" % (filename,))

            path, filename = os.path.split(filename)
            self.graph = sqliteBackedGraph(path, filename)

        self._open = True

    def query(self, rest, initNs=None, initBindings=None):
        """
        Execute a SPARQL query and get the results as a SPARQLResult

        {rest} is a string that should begin with "SELECT ", usually
        """
        assert self._open

        if initNs is None:
            initNs = dict(self.graph.namespaces()) 
        if initBindings is None: initBindings = {}

        sel = select(self.getBase(), rest)
        ret = self.graph.query(sel, initNs=initNs, initBindings=initBindings,
                DEBUG=False)
        return ret

    def getBase(self):
        d = dict(self.graph.namespaces())
        return d.get('', RDFSNS)

    def addTriple(self, s, v, *objects):
        """
        Make a statement/arc/triple in the database.

        Strings, ints and floats as s or o will automatically be coerced to
        RDFLiteral().  It is an error to give a RDFLiteral as v, so no
        coercion will be done in that position.

        2-tuples will be coerced to bnodes.
        
        If more than one object is given, i.e.
            addTriple(a, b, c1, c2, c3) 
        this is equivalent to:
            addTriple(a,b,c1); addTriple(a,b,c2); addTriple(a,b,c3)
        """
        assert self._open
        assert len(objects) >= 1, "You must provide at least one object"
        if canBeLiteral(s):
            s = RDFLiteral(s)

        bnode = None
        for o in objects:
            if canBeLiteral(o):
                o = RDFLiteral(o)
            elif isinstance(o, tuple) and len(o) == 2:
                if bnode is None:
                    bnode = BNode()
                self.addTriple(bnode, *o)
                o = bnode

            assert None not in [s,v,o]
            self.graph.add((s, v, o))

    def dump(self):
        assert self._open
        io = StringIO()
        try:
            self.graph.serialize(destination=io, format='n3')
        except Exception, e:
            import sys, pdb; pdb.post_mortem(sys.exc_info()[2])
        return io.getvalue()

    def extendGraphFromFile(self, graphFile):
        """
        Add all the triples in graphFile to my graph

        This is done as if the loaded graph is the same context as this
        database's graph, which means <> from the loaded graph will be
        modified to mean <> in the new context
        """
        assert self._open
        extendGraphFromFile(graphFile)

    def extendGraph(self, graph):
        """
        Add all the triples in graph to my graph
        """
        assert self._open
        TriplesDatabase.extendRawGraph(self.graph, graph)

    @classmethod
    def extendRawGraph(cls, orig, additional):
        # add each triple
        # FIXME - this should use addN
        for s,v,o in additional:
            orig.add((s,v,o))

    def commit(self):
        assert self._open
        self.graph.commit()


def randomPublicID():
    """
    Return a new, random publicID
    """
    return 'file:///%s' % (hashlib.md5(str(random.random())).hexdigest(),)


def sqliteBackedGraph(path, filename):
    """
    Open previously created store, or create it if it doesn't exist yet.
    """
    from pysqlite2.dbapi2 import OperationalError
    from rdflib import plugin
    from rdflib.store import Store, VALID_STORE

    # Get the sqlite plugin. You may have to install the python sqlite libraries
    store = plugin.get('SQLite', Store)(filename)

    rt = store.open(path, create=False)

    if rt != VALID_STORE:
        try:
            # There is no underlying sqlite infrastructure, create it
            rt = store.open(path, create=True)
            assert rt == VALID_STORE
        except OperationalError, e:
            raise
            import sys, pdb; pdb.post_mortem(sys.exc_info()[2])
     
    # There is a store, use it
    return Graph(store)


class rdfIsInstance(rdfAbstract):
    """
    An rdfalchemy descriptor that makes a boolean out of Bar in this
    construction:

        :Bar a rdfs:Class .
        :foo a :Bar.

    Does *not* check for is-a semantics at this point - just exact boolean
    match on that class.
    """
    range_type = None

    def __init__(self, classToCheck):
        self.klass = classToCheck 
 
    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self.klass in obj.__dict__:
            return obj.__dict__[self.klass]
        ret = list(obj.db.triples((obj.resUri, RDF_a, self.klass))) and True or False 
        obj.__dict__[self.klass] = ret
        return ret
 
    def __set__(self, obj, true_false):
        """
        Create the triple for obj
        """
        obj.__dict__[self.klass] = true_false
        obj.db.set((obj.resUri, self.klass, true_false))

    def __delete__(self, obj):
        if obj.__dict__.has_key(self.klass):
            del obj.__dict__[self.klass]
        for s,p,o in obj.db.triples((obj.resUri, RDF_a, self.klass)):
            obj.db.remove((s,p,o))


class rdfSingleDefault(rdfSingle):
    """
    rdfSingle that can return a default value by calling the "default"
    argument with an instance of the subject.
    """
    def __init__(self, pred, default=None, cacheName=None, range_type=None):
        super(rdfSingleDefault, self).__init__(pred, cacheName, range_type)
        assert callable(default), "default must be a callable object"
        self._defaultCallable = default

    def __get__(self, obj, cls):
        r = super(rdfSingleDefault, self).__get__(obj, cls)
        if r is None:
            return self._defaultCallable(obj)
        return r


class rdfsPTClass(rdfsClass):
    """
    Similar to rdfalchemy.rdfsSubject.rdfsClass but when .label is missing
    default to iriToTitle(resUri)
    """
    label = rdfSingleDefault(RDFSNS.label, lambda o: iriToTitle(o.resUri))


def extendGraphFromFile(inGraph, graphFile, format='n3'):
    """
    Add all the triples in graphFile to inGraph

    This is done as if the loaded graph is the same context as this
    database's graph, which means <> from the loaded graph will be
    modified to mean <> in the new context
    """
    g2 = Graph()

    # Generate a random publicID, then later throw it away, by
    # replacing references to it with URIRef('').  extendGraphFromFile thus
    # treats the inserted file as if it were part of the original file
    publicID = randomPublicID()
    g2.load(graphFile, format=format, publicID=publicID)

    # add each triple
    # FIXME - this should use addN
    for s,v,o in g2:
        if s == URIRef(publicID):
            inGraph.add((URIRef(''), v, o))
        else:
            inGraph.add((s,v,o))
