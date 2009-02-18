"""
Test the database and object mapping abilities of playtools.sparqly
"""
import os

import rdflib

from twisted.trial import unittest
from twisted.python.util import sibpath

from rdflib.Namespace import Namespace
from rdflib import Literal, URIRef, BNode

from playtools import sparqly, util
from playtools.test.pttestutil import IsomorphicTestableGraph
from playtools.common import this, RDFSNS, a

class Employee(sparqly.SparqItem):
    firstname = sparqly.Literal("SELECT ?f { $key :firstname ?f }")
    nickname = sparqly.Literal("SELECT ?n { $key :nickname ?n }")
    lastname = sparqly.Literal("SELECT ?l { $key :lastname ?l }"
            ).setTransform(lambda l: str(l).upper())
    straightShooter = sparqly.Boolean(
            """ASK { $key a
            :StraightShooterWithUpperManagementWrittenAllOverHim . }""")
    brokenStraightShooter = sparqly.Boolean(
            """SELECT ?x { $key a 
            :StraightShooterWithUpperManagementWrittenAllOverHim }""")

Employee.middlename = sparqly.Literal("SELECT ?m { $key :middlename ?m}",
        default=Employee.nickname)

Employee.supervisor = sparqly.Ref(Employee, "SELECT ?s { $key :supervisor $s }")

STAFF = Namespace('http://corp.com/staff#')
ANS = Namespace('http://a#')
BNS = Namespace('http://b#')

TESTING_NAMESPACES = {'a': ANS, 'b': BNS }


class SparqlyTestCase(unittest.TestCase):
    def test_select(self):
        """
        Select generates select strings and not something else, such as
        cheeseburgers.
        """
        sel = sparqly.select(base="http://corp.com/staff", rest="SELECT ?x { ?x a :ninja }")
        self.assertEqual(sel, "BASE <http://corp.com/staff> SELECT ?x { ?x a :ninja }")

    def test_iriToTitle(self):
        """Pull fragment ids out of URIs"""
        title1 = sparqly.iriToTitle('foo#hi')
        title2 = sparqly.iriToTitle('foo#hi#zam')
        title3 = sparqly.iriToTitle('foozam')
        title4 = sparqly.iriToTitle('#foozam')
        title5 = sparqly.iriToTitle('#foozam zam')
        
        self.assertEqual(title1, 'Hi')
        # the next one looks odd, but this appears to be what Firefox
        # does, so imitate that.
        self.assertEqual(title2, 'Hi#Zam')
        self.assertEqual(title3, '')
        self.assertEqual(title4, 'Foozam')
        self.assertEqual(title5, 'Foozam Zam')

    def test_sparqItem(self):
        """
        verify the orm works
        """
        db = sparqly.TriplesDatabase()
        db.graph = rdflib.ConjunctiveGraph()
        # hack so there's a blank (base) namespace
        db.graph.bind('', STAFF)

        # hack to pretend the database is on disk somewhere
        db._open = True
        g = rdflib.ConjunctiveGraph()

        corp = sibpath(__file__, 'corp.n3')
        g.load(corp, format='n3')
        db.extendGraph(g)

        peter = Employee(db=db, key=STAFF.e1230)
        self.assertEqual(peter.firstname, 'Peter')
        self.assertEqual(peter.lastname, 'GIBBONS')
        self.assertEqual(peter.middlename, '"The Gib"')
        self.assertEqual(peter.label, u'E1230')

        self.assertRaises(sparqly.BooleanNeedsASKQueryError, getattr, peter, 'brokenStraightShooter')

        bill = peter.supervisor[0]
        self.assertEqual(bill.lastname, 'LUMBERGH')

        self.assertEqual(peter.straightShooter, True)
        self.assertEqual(bill.straightShooter, False)



class TriplesDbTestCase(unittest.TestCase):

    def fill(self, graph):
        """
        Add some triples to a graph (without using addTriple)
        """
        graph.bind('a', Namespace('http://a#'))
        graph.bind('b', Namespace('http://b#'))
        graph.add((URIRef('http://a#x'), URIRef('http://a#y'),
            Literal(1)))
        graph.add((URIRef('http://b#xb'), URIRef('http://b#yb'),
            Literal(2)))
        graph.add((URIRef('http://a#x'), URIRef('http://b#y'),
            Literal(3)))
        graph.add((this, this, Literal(4)))

    def setUp(self):
        """
        Create an empty triples database
        """
        self.db = sparqly.TriplesDatabase()
        self.db.open(None, graphClass=IsomorphicTestableGraph)

    def test_query(self):
        """
        Try some queries against a fake graph
        """
        self.db.open(None)
        self.fill(self.db.graph)

        ret = list(self.db.query("SELECT ?a { ?a b:yb 2 }"))
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], URIRef('http://b#xb'))

        ret = sorted(self.db.query("SELECT ?b { a:x ?b [] }"))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret[0][0], URIRef('http://a#y'))

        ret = sorted(self.db.query("SELECT ?b { a:x ?b 69 }"))
        self.assertEqual(len(ret), 0)

        q = lambda: sorted(self.db.query("SELECT ?b { 1 2 3 }"))
        self.assertRaises(SyntaxError, q)

    def test_canBeLiteral(self):
        can = sparqly.canBeLiteral

        bnode = BNode()
        lit = Literal(1)
        uri = URIRef("http://hi")
        self.failIf(can(uri))
        self.failIf(can(lit))
        self.failIf(can(bnode))
        self.failUnless(can(1))
        self.failUnless(can(1.1))
        self.failUnless(can(''))
        self.failUnless(can(u''))

    def test_addTriple(self):
        """addTriple should handle URIRefs, automatically coerce literals, and
        automatically coerce tuples to bnodes
        """
        comp1 = IsomorphicTestableGraph()
        for p, ns in TESTING_NAMESPACES.items():
            comp1.bind(p, ns)

        self.fill(comp1)
        self.fill(self.db.graph)

        self.assertEqual(comp1, self.db.graph)

        self.db.addTriple(STAFF.e1231, STAFF.firstname, 'Michael')
        self.db.addTriple(STAFF.e1231, STAFF.lastname, 'Bolton')
        self.db.addTriple(STAFF.e1231, STAFF.supervisor, STAFF.e1001)

        comp1.add((STAFF.e1231, STAFF.firstname, Literal('Michael')))
        comp1.add((STAFF.e1231, STAFF.lastname, Literal('Bolton')))
        comp1.add((STAFF.e1231, STAFF.supervisor, STAFF.e1001))

        self.assertEqual(comp1, self.db.graph)

        comp1.add((STAFF.e1232, STAFF.firstname, Literal('Samir')))
        comp1.add((STAFF.e1232, STAFF.firstname, Literal('Nina')))

        self.db.addTriple(STAFF.e1232, STAFF.firstname, 'Samir', 'Nina')

        self.assertEqual(comp1, self.db.graph)

        bn = BNode()
        comp1.add((STAFF.e1230, STAFF.salary, bn))
        comp1.add((bn, a, STAFF.ExemptEmployee))
        comp1.add((bn, STAFF.annualSalary, Literal(45000)))

        self.db.addTriple(STAFF.e1230, STAFF.salary, 
                (a, STAFF.ExemptEmployee), (STAFF.annualSalary, 45000))

        self.assertEqual(comp1, self.db.graph)

    def test_dump(self):
        assert 0

    test_dump.todo = "Add some triples to a graph, dump, examine the string"

    def test_extendGraphFromFile(self):
        """
        extendGraphFromFile should add triples to the db's graph, within the context
        of the db's graph's publicID.  Show that:
        - old triples are still around
        - new triples exist
        - <> is not rewritten as <newpublicid.n3>
        """
        self.db.open(None)
        self.fill(self.db.graph)
        self.db.extendGraphFromFile(sibpath(__file__, 'extend.n3'))
        trips = list(self.db.graph)
        # old triples still around
        self.failUnless((ANS.x, ANS.y, Literal(1)) in trips)
        # new triple is around as well, and this is still this
        self.failUnless((this, ANS.f, ANS.g) in trips)

    def test_open(self):
        newdb = sparqly.TriplesDatabase()
        q = lambda: list(newdb.query("SELECT ?a { ?a b:yb 2 }"))
        self.assertRaises(AssertionError, q)
        newdb.open(None)
        self.fill(newdb.graph)
        ret = list(newdb.query("SELECT ?a { ?a b:yb 2 }"))
        self.assertEqual(len(ret), 1)

    def test_sqlite(self):
        path = os.getcwd()
        filename = 'test.db'
        _ignored = sparqly.sqliteBackedGraph(path, filename)
        self.db.open(path + '/' + filename)
        self.fill(self.db.graph)
        self.db.addTriple(STAFF.e1231, STAFF.firstname, 'Michael')
        self.db.commit()
        del self.db
        self.setUp()
        self.db.open('test.db')
        ret = sorted(self.db.query("SELECT ?c { <http://corp.com/staff#e1231> ?b ?c }"))
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], Literal('Michael', datatype=rdflib.URIRef('NULL')))

