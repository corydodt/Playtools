from playtools import sparqly as S
from rdflib.Namespace import Namespace
from rdfalchemy import rdfSingle, rdfMultiple, rdfList, rdfsSubject
from rdfalchemy.orm import mapper

FUN = Namespace('file:///home/cdodt/wc/Playtools/doc/fun.n3#')
RDF = Namespace('http://fake.org/rdf#')

class Attack(rdfsSubject):
    rdf_type = FUN.Attack
    value = rdfList(RDF.value)
    def __str__(self):
        "ATTACK for %s" % (self.value,)

class Monster(rdfsSubject):
    name = rdfSingle(FUN.name)
    attack = rdfList(FUN.attack, range_type=FUN.Attack)

mapper()

rdfsSubject.db.load('fun.n3', format='n3')


for m in Monster.ClassInstances():
    print m.attack
    for k in m.attack:
        # FIXME - doesn't work for a list of bnodes of type Attack
        print k.value
