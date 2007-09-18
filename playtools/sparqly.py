"""
========
SPARQL-y
========

A really stupid SPARQL O*M (OSTM? object-semantic triple mapper.)

Inspired by, but not really resembling, Divmod Axiom.

Defining Objects and their Attributes
=====================================

The object side of the API is the SparqItem.  Create a subclass of this to
represent your item:

class Employee(SparqItem):
    ...

Next determine which attributes of Employee you want to represent.  These can
be any relationships you can connect to an Employee-typed subject.  You might
choose firstname, lastname, supervisor.  You use Attributes to
represent these.  Attributes represent a query that retrieves the related data
for an instance of that object.

Here's how you would construct firstname and lastname on Employee:

class Employee(SparqItem):
    firstname = Literal("SELECT ?f { $key :firstname ?f }")
    lastname = Literal("SELECT ?l { $key :lastname ?l }").setTransform(lambda n: n.upper())


Note two things:
    1) You have to write the SPARQL query that gets the item
    2) The SPARQL query must contain $key to show how the attribute relates
       to the Employee (your subclass of SparqItem).
    3) Literal (and Key) have a setTransform() method which takes a 1-arg
       callable that can modify the value after it is retrieved.  For one use
       of this, see how the SparqItem.label attribute is defined below.

Now let's add supervisor.  This is an attribute that actually refers to
another item of the same type, Employee.

class Employee(SparqItem):
    firstname = Literal("SELECT ?f { $key :firstname ?f }")
    lastname = Literal("SELECT ?l { $key :lastname ?l }")
    supervisor = Ref(Employee, "SELECT ?sup { $key :supervisor ?sup }")

Well that was easy.  The Ref attribute returns a list of Employee
when accessed, which will usually have just one item, the employee's immediate
supervisor.  (But it could return the list of all eight of your bosses.)

Finally, the Key attribute type returns the key of the thing you are
selecting, as an IRI string.


Using Objects
=============
Assume we have:

class Employee(SparqItem):
    firstname = Literal("SELECT ?f { $key :firstname ?f }")
    lastname = Literal("SELECT ?l { $key :lastname ?l }").setTransform(lambda n: n.upper())
# need to define this after because it refers to a class that isn't defined
# yet
Employee.supervisor = Ref(Employee, "SELECT ?s { $key :supervisor $s }")

>>> staff = Namespace('http://corp.com/staff#')
>>> cg = rdflib.Graph()
>>> cg.load(...)
>>> 
>>> emp = Employee(db=cg, key=staff.e1230)
>>> print emp.firstname, emp.lastname
Peter GIBBONS
>>> # look, lastname is uppercased thanks to our setTransform. :)
>>> super = emp.supervisor
>>> print super.firstname, super.lastname
Bill LUMBERGH


Limitations:
    - There is no cache.  A SPARQL query must be issued against the data
      *every* time the application wants the value.
    - There is no schema discovery.  Future idea: It may be possible to use
      OWL/RDFS to describe object-oriented relationships, and read them into
      your Python classes.
    - The constructor for Attributes is terrible.  It assumes you have set up
      prefixes correctly on the TriplesDatabase, and it assumes you want to
      learn SPARQL.  :-)
    - Assignment (TODO) - currently can't be done at all.  I don't know how
      assignment to Ref will work, since it returns a list.  Assignment to
      Literal shouldn't be too hard.
    - As illustrated above, recursive relationships are awkward.  To make
      supervisor, we had to define the attribute after defining the SparqItem.

"""

from string import Template

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


from rdflib import URIRef, BNode
from rdflib.Graph import Graph
from rdflib.Literal import Literal as RDFLiteral

from playtools.common import RDFSNS


def select(base, rest):
    d = dict(base=base, rest=rest, )
    return """BASE <%(base)s> %(rest)s""" % d


def iriToTitle(iri):
    """Return the fragment id of the iri, in title-case"""
    if '#' not in iri:
        return ''
    uri = iri.lstrip('<').rstrip('>')
    return uri.split('#', 1)[1].title()


NODEFAULT = ()


class SparqAttribute(object):
    """One attribute on a SparqItem, denoting type
    """
    def __init__(self, selector, default=NODEFAULT):
        self.selector = Template(selector)
        self.default = default

    def solve(self, db, key):
        """Return the value or values of this attribute."""
        data = self.retrieveData(db, key)
        if data is None or len(data) == 0:
            return None
        assert len(data) == 1
        return data[0]

    def retrieveData(self, db, key):
        """Do my query against a db and return its result list.
        If no result list and default is set, return default.
        """
        # rdflib.URIRef could be passed as key; handle that case
        if hasattr(key, 'n3'):
            key = key.n3()

        rest = self.selector.safe_substitute(key=key)
        data = [r[0] for r in db.query(rest)]  ## TODO - support multiple variable queries? probably not
        if len(data) == 0:
            if self.default is NODEFAULT:
                return None

            if isinstance(self.default, SparqAttribute):
                return self.default.solve(db, key)

            return [self.default]
        return data


class Ref(SparqAttribute):
    """
    An item that must be loaded via another SparqItem
    """
    def __init__(self, itemClass, selector):
        self.itemClass = itemClass
        self.selector = selector
        super(Ref, self).__init__(selector)

    def solve(self, db, key):
        data = self.retrieveData(db, key)

        if data is None:
            return []

        ret = []
        cls = self.itemClass

        for i in data:
            assert isinstance(i, URIRef) or isinstance(i, BNode), (
                    "This query returned literals, not URIs!\n-- %s" % (i,))
            # pull the uri string from each data item
            att = cls(db=db, key=i.n3())
            ret.append(att)

        return ret


class LeafAttribute(SparqAttribute):
    """
    An attribute that returns some kind of literal when accessed, including
    the string representation of something other than a Literal (e.g. Key).

    LeafAttributes can return a modified representation if you call
    setTransform on them.
    """
    def __init__(self, *a, **kw):
        self.transform = None
        super(LeafAttribute, self).__init__(*a, **kw)

    def setTransform(self, transform):
        """
        transformer is a 1-argument callable that will be called when
        solve'ing for this attribute

        Returns self so you can call it in a class scope while defining the
        attribute
        """
        self.transform = transform
        return self

    def solve(self, db, key):
        data = super(LeafAttribute, self).solve(db, key)
        if self.transform is not None:
            return self.transform(data)
        return data


class Literal(LeafAttribute):
    """An attribute that returns as a rdflib.Literal"""


class Key(LeafAttribute):
    """
    An attribute that returns the IRI for the SparqItem that has it as an
    attribute, as a string.
    """
    def __init__(self, transform=None):
        self.transform = transform
        super(Key, self).__init__('')

    def solve(self, db, key):
        if self.transform:
            key = self.transform(key)
        return [key]


class SparqItem(object):
    """An item composed of SPARQL queries against the store.
    Built out of SparqAttributes like this:

    class Thinger(SparqItem):
        slangName = Literal("SELECT ?slang $datasets { $key :slangName ?slang }")

    >>> myThinger = Thinger(db=someTriplesDatabase, key=':marijuana')
    >>> myThinger.slangName
    "Wacky Tabacky"
     
    """
    label = Literal(
        'SELECT ?l { $key rdfs:label ?l }', default=Key().setTransform(iriToTitle))
    comment = Literal('SELECT ?d { $key rdfs:comment ?d }', default='')

    def __init__(self, db, key):
        self.db = db
        self.key = key

    def __getattribute__(self, k):
        real = super(SparqItem, self).__getattribute__(k)
        if isinstance(real, SparqAttribute):
            return real.solve(db=self.db, key=self.key)
        return real

    def __repr__(self):
        try:
            l = self.label
        except:
            l = ''
        return '<%s %s>' % (self.__class__.__name__, l)


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
    def __init__(self, base, prefixes, datasets, graph=None):
        self.base = base
        self.prefixes = {'rdfs': RDFSNS}
        self.prefixes.update(prefixes)

        if graph is None:
            self.graph = Graph()
        else:
            self.graph = graph

        for d in filterNamespaces(datasets):
            self.graph.load(d, format='n3')

        for pfx, uri in self.prefixes.items():
            self.graph.bind(pfx, uri)
                
    def query(self, rest):
        """
        Execute a SPARQL query and get the results as a SPARQLResult

        {rest} is a string that should begin with "SELECT ", usually
        """
        sel = select(self.base, rest)
        ret = self.graph.query(sel, initNs=self.prefixes)
        return ret

    def addTriple(self, s, v, *objects):
        """
        Make a statement/arc/triple in the database.

        Strings, ints and floats as s or o will automatically be coerced to
        RDFLiteral().  It is an error to give a RDFLiteral as v, so no
        coercion will be done in that position
        
        If more than one object is given, i.e.
            addTriple(a, b, c1, c2, c3) 
        this is equivalent to:
            addTriple(a,b,c1); addTriple(a,b,c2); addTriple(a,b,c3)
        """
        assert len(objects) >= 1, "You must provide at least one object"
        if canBeLiteral(s):
            s = RDFLiteral(s)

        for o in objects:
            if canBeLiteral(o):
                o = RDFLiteral(o)
            assert None not in [s,v,o]
            self.graph.add((s, v, o))

    def dump(self):
        io = StringIO()
        try:
            self.graph.serialize(destination=io, format='n3')
        except Exception, e:
            import sys, pdb; pdb.post_mortem(sys.exc_info()[2])
        return io.getvalue()
