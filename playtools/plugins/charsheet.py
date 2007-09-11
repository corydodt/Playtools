
from playtools.interfaces import ICharSheetSection
from zope.interface import Interface, implements
from twisted.plugin import IPlugin
from rdflib.Namespace import Namespace as NS
from rdflib.sparql.bison import Parse

rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')
rdf = NS("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
fam = NS('http://thesoftworld.com/2007/family.n3#')
char = NS('http://thesoftworld.com/2007/characteristic.n3#')
dice = NS('http://thesoftworld.com/2007/dice.n3#')
pcclass = NS('http://thesoftworld.com/2007/pcclass.n3#')
prop = NS('http://thesoftworld.com/2007/property.n3#')
play = NS('http://thesoftworld.com/2007/player.n3#')

NAMESPACES = {
    'fam':fam,
    'char':char,
    'dice':dice,
    'prop':prop,
    'pcclass':pcclass,
    'rdfs':rdfs,
    'rdf':rdfs,
    'player':play,
}

def bonus(x):
    return (int(x)/2)-5

class PlayerName(object):
    """
    Discover the players name.
    """
    implements(ICharSheetSection, IPlugin)

    def getName(self, graph, player):
        data = list(graph.query("""SELECT ?name {
                ?player player:name ?name.
        }""", {'?player':player}, initNs=NAMESPACES))
        if not data:
            raise KeyError, 'No data'
        return data[0][0]

    def asText(self, graph, player):
        name = self.getName(graph, player)
        print 'Player name:', name

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
        SELECT ?weapon ?name ?damage {
                ?player player:wields ?weapon.
                ?weapon rdfs:label ?name.
                ?weapon player:damage ?damage.
        }""")
    attack_stmt = Parse("""
        SELECT ?attack {
                ?weapon player:attacks ?attack;
        }""")

    def weapons(self, graph, player):
        return graph.query(self.weapon_stmt, {'?player':player}, initNs=NAMESPACES)

    def attacks(self, graph, weapon):
        data = list(graph.query(self.attack_stmt, {'?weapon':weapon}, initNs=NAMESPACES))
        if len(data) != 1:
            return ''
        return '/'.join(graph.items(data[0][0]))
        
    def asText(self, graph, player):
        for weapon, name, damage in self.weapons(graph, player):
            print name, self.attacks(graph, weapon), damage

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

playerName = PlayerName()
statBlock = StatBlock()
weapons = Weapons()
skills = Skills()
