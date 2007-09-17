
from playtools.interfaces import ICharSheetSection
from zope.interface import Interface, implements
from twisted.plugin import IPlugin
from rdflib.Namespace import Namespace as NS
from rdflib import URIRef
from rdflib.sparql.bison import Parse

rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')
rdf = NS("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
fam = NS('http://thesoftworld.com/2007/family.n3#')
char = NS('http://thesoftworld.com/2007/characteristic.n3#')
dice = NS('http://thesoftworld.com/2007/dice.n3#')
pcclass = NS('http://thesoftworld.com/2007/pcclass.n3#')
prop = NS('http://thesoftworld.com/2007/property.n3#')
player = NS('http://thesoftworld.com/2007/player.n3#')
character = NS('http://thesoftworld.com/2007/character.n3#')
weapon = NS('http://thesoftworld.com/2007/weapon.n3#')

NAMESPACES = {
    'fam':fam,
    'char':char,
    'dice':dice,
    'prop':prop,
    'pcclass':pcclass,
    'rdfs':rdfs,
    'rdf':rdfs,
    'player':player,
    'character':character,
    'weapon':weapon,
}

def bonus(x):
    return (int(x)/2)-5

class PersonalInfo(object):
    """
    Discover the character name.
    """
    implements(ICharSheetSection, IPlugin)

    statement = Parse(""" SELECT ?data { ?character ?info ?data } """)

    def getData(self, graph, character, info):
        query = graph.query(self.statement,
            {'?character':character, '?info':info}, 
            initNs=NAMESPACES)
        for (data,) in query:
            return data
        raise KeyError, 'No data'
    
    def collectData(self, graph, character):
        for info in [
            URIRef(player + 'name')
            ]:
            try:
                label, data = self.getData(graph, character, info)
                yield info, data
            except KeyError:
                pass

    def asText(self, graph, character):
        for info, data in self.collectData(graph, character):
            print info, data

class StatBlock(object):
    """
    Get the D20 style stat block.
    """
    implements(ICharSheetSection, IPlugin)

    def stats(self, graph, player):
        data = list(graph.query("""SELECT ?str ?dex ?con ?int ?wis ?cha { 
                ?player char:str ?str.
                ?player char:dex ?dex.
                ?player char:con ?con.
                ?player char:int ?int.
                ?player char:wis ?wis.
                ?player char:cha ?cha.
        }""", {'?player':player}, initNs=NAMESPACES))
        if not data:
            raise KeyError
        return data[0]
        
    def asText(self, graph, player):
        str, dex, con, int, wis, cha = self.stats(graph, player)
        print 'Str:', str, bonus(str)
        print 'Dex:', dex, bonus(dex)
        print 'Con:', con, bonus(con)
        print 'Wis:', wis, bonus(wis)
        print 'Int:', int, bonus(int)
        print 'Cha:', cha, bonus(cha)
        
class Weapons(object):
    implements(ICharSheetSection, IPlugin)

    weapon_stmt = Parse("""
        SELECT ?weapon ?name ?damage ?attacks {
            ?character character:wields [
                rdfs:label ?name; 
                weapon:damage ?damage;
            ].
        }""")

    def weapons(self, graph, character):
        return graph.query(self.weapon_stmt, 
                {'?character':character}, initNs=NAMESPACES)

    def attacks(self, graph, attacks):
        return '/'.join(graph.items(attacks))
        
    def asText(self, graph, player):
        for weapon, name, damage, attacks in self.weapons(graph, player):
            print name, self.attacks(graph, attacks), damage

class Skills(object):
    """
    Expects data of this form::

        @prefix player: <http://thesoftworld.com/2007/player.n3#> .
        @prefix c: <http://thesoftworld.com/2007/characteristic.n3#> .
        @prefix s: <http://thesoftworld.com/2007/skill.n3#> .
        :somePlayer 
            c:str 10;
            player:hasSkill [ player:skill s:hide; player:skillRanks 4; ]
        .
    """
    implements(ICharSheetSection, IPlugin)

    statement = Parse(
                """SELECT ?label ?abilityName ?ranks ?abilityScore {
                ?player 
                    player:hasSkill [
                        player:skill [ 
                            rdfs:label ?label; 
                            prop:keyAbility ?ability 
                        ];
                        player:skillRanks ?ranks;
                    ];
                    ?ability ?abilityScore
                .
                ?ability rdfs:label ?abilityName.
            }""")

    def getSkills(self, graph, player):
        """
        @return: (label, abilityName, total, abilityBonus, ranks, acp)
        """
        for label, abilityName, ranks, abilityScore in graph.query(
                self.statement, {'?player':player}, initNs=NAMESPACES):
            abilityBonus = bonus(int(abilityScore))
            ranks = int(ranks)
            # TODO: Armor check penalty.
            acp = 0
            yield label, abilityName, abilityBonus + ranks + acp, abilityBonus, ranks, acp
        
    def asText(self, graph, player):
        """
        Will calculate the bonus for a skill and output like::

            Hide (Dex): 9 = 5 + 4 + 0

        TODO: Armor check penalties.
        """
        for label, abilityName, total, abilityBonus, ranks, acp in self.getSkills(graph, player):
            print "%s (%s): %d = %d + %d + %d" % (label, abilityName, total, abilityBonus, ranks, acp)

personalInfo = PersonalInfo()
statBlock = StatBlock()
weapons = Weapons()
skills = Skills()
