
import sqlite3
from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib.Namespace import Namespace as NS
from rdflib.Identifier import Identifier
from rdflib.Literal import Literal
from rdflib.BNode import BNode
import itertools
import sys

from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers

ns_fam = NS('http://thesoftworld.com/2007/family.n3#')
ns_char = NS('http://thesoftworld.com/2007/characteristic.n3#')
ns_dice = NS('http://thesoftworld.com/2007/dice.n3#')
ns_pcclass = NS('http://thesoftworld.com/2007/pcclass.n3#')
ns_prop = NS('http://thesoftworld.com/2007/properties.n3#')
ns_skill = NS("http://thesoftworld/2007/skills.n3#")
ns_spell = NS("http://thesoftworld/2007/spells.n3#")
ns_rdf = NS("http://www.w3.org/2000/01/rdf-schema#")
ns_monster = NS("http://thesoftworld/2007/monsters.n3#")

a = ns_rdf['typeof']

from playtools.convert import rdfName

def rdfClass(s):
    return ':' + ''.join(p.capitalize() for p in s.split())

class Converter(object):
    def load(self, conn):
        self.alldata = list(self.data(conn))

    def dump(self, f):
        assert self.alldata, ".load() not called"
        for line in itertools.chain(self.preamble(), self.classes(), self.alldata):
            print >>f, line
            print line

    def preamble(self): 
        raise NotImplemented

    def classes(self):
        raise NotImplemented

class Skills(Converter):

    def preamble(self):
        return [
            "@prefix : <http://thesoftworld/2007/skills.n3#>.",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            '@prefix c: <http://thesoftworld.com/2007/characteristic.n3#> .',
            '<> rdfs:title "DND3.5E skills" .',
            '<> rdfs:comment "Exported from srd35.db" .',
        ]

    def classes(self):
        return [
            ":Skill a rdfs:Class .",
            ":SkillProperty a rdfs:Class .",
            ":TrainedSkill rdfs:subclassOf rdfs:Class .",
            ":UntrainedSkill rdfs:subclassOf rdfs:Class .",
            ":ArmorCheck rdfs:subclassOf rdfs:Class .",
            ":Psionic rdfs:subclassOf rdfs:Class .",
        ]

    def data(self, conn):
        c = conn.cursor()

        c.execute('''select 
                name, subtype, key_ability, psionic, trained, armor_check,
                description, skill_check, action, try_again, special, restriction,
                synergy, epic_use, untrained, full_text, reference 
                from skill''')

        for (name, subtype, key_ability, psionic, trained, armor_check, description,
             skill_check, action, try_again, special, restriction, synergy, epic_use,
             untrained, full_text, reference) in c:
            yield '%s a :Skill;' % rdfName(name)
            if trained == 'Yes':
                yield '    a :TrainedSkill;'
            if untrained == 'Yes':
                yield '    a :UntrainedSkill;'
            if armor_check == 'Yes': 
                yield '    a :ArmorCheck;'
            if psionic == 'Yes':
                yield '    a :PsionicSkill;'
            yield '    rdfs:label """%s""";' % name.encode('utf-8')
            yield '    :keyAbility c%s;' % rdfName(key_ability)
            if subtype:
                yield '    :subType %s;' % ', '.join(rdfName(st) for st in subtype.split(','))
            yield '.'

        c.close()

class Monsters(Converter):

    def preamble(self):
        return [
            "@prefix : <http://thesoftworld/2007/monsters.n3#>.",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            '@prefix c: <http://thesoftworld.com/2007/characteristic.n3#> .',
            '@prefix p:     <http://thesoftworld.com/2007/properties.n3#> .',
            '<> rdfs:title "DND3.5E monsters" .',
            '<> rdfs:comment "Exported from srd35.db" .',
        ]

    def classes(self):
        return [
        ":Monster a rdfs:Class .",

        ":MonsterType a rdfs:Class .",
        ":MonsterousHumanoid rdfs:subclassOf :MonsterType .",
        ":Construct rdfs:subclassOf :MonsterType .",
        ":Undead rdfs:subclassOf :MonsterType .",
        ":Outsider rdfs:subclassOf :MonsterType .",
        ":MagicalBeast rdfs:subclassOf :MonsterType .",
        ":Vermin rdfs:subclassOf :MonsterType .",
        ":Dragon rdfs:subclassOf :MonsterType .",
        ":Elemental rdfs:subclassOf :MonsterType .",
        ":Ooze rdfs:subclassOf :MonsterType .",
        ":Aberration rdfs:subclassOf :MonsterType .",
        ":MonstrousHumanoid rdfs:subclassOf :MonsterType .",
        ":Fey rdfs:subclassOf :MonsterType .",
        ":Animal rdfs:subclassOf :MonsterType .",
        ":Plant rdfs:subclassOf :MonsterType .",
        ":Humanoid rdfs:subclassOf :MonsterType .",
        ":Giant rdfs:subclassOf :MonsterType .",
        ]

    def data(self, conn):
        c = conn.cursor()
        c.execute('''select 

    family, name, altname, size, type, descriptor, hit_dice,
    initiative, speed, armor_class, base_attack, grapple, attack, full_attack,
    space, reach, special_attacks, special_qualities, saves, abilities, skills,
    bonus_feats, feats, epic_feats, environment, organization, challenge_rating,
    treasure, alignment, advancement, level_adjustment, special_abilities,
    stat_block, full_text, reference

                from monster''')

        for (family, name, altname, size, type, descriptor, hit_dice,
                initiative, speed, armor_class, base_attack, grapple, attack,
                full_attack, space, reach, special_attacks, special_qualities,
                saves, abilities, skills, bonus_feats, feats, epic_feats,
                environment, organization, challenge_rating, treasure, alignment,
                advancement, level_adjustment, special_abilities, stat_block,
                full_text, reference) in c:

            # remove some trashy names
            if '-Level' in name:
                continue
            if '(' in name:
                continue

            yield '%s a :Monster;' % rdfName(name)
            yield '    p:family %s;' % rdfName(family)
            yield '    rdfs:label """%s""";' % name.encode('utf-8')
            if altname:
                yield '    rdfs:label """%s""";' % altname.encode('utf-8')
            if size == 'Colossal+':
                size = 'Colossal'
            yield '    p:size c%s;' % rdfName(size)
            yield '    a %s;' % rdfClass(type)
            if descriptor:
                yield '    :descriptor %s;' % ', '.join(rdfName(dsc) for dsc in descriptor.split(','))
            yield '    p:hitPoints """%s""";' % hit_dice.split()[0]
            yield '    p:initiative %d;' % int(initiative.split()[0])
            
            # speed, oh god.

            yield self.calcAC(armor_class)

            # armor_class
            # base_attack
            # grapple
            # attack

            # full_attack
            # space
            # reach
            # special_attacks
            # special_qualities

            # saves
            # abilities
            # skills
            # bonus_feats
            # feats
            # epic_feats

            # environment
            # organization
            # challenge_rating
            # treasure
            # alignment

            # advancement
            # level_adjustment
            # special_abilities
            # stat_block

            # full_text
            # reference

            yield '.'


        c.close()

    def calcAC(self, armor_class):
        ac, touch, flat = armor_class.rsplit(',', 2)
        ac = int(ac.split()[0])
        touch = int(touch.split()[1])
        flat = int(flat.split()[1])
        return '    p:armorClass [ a :ACGroup; :ac %d; :touch %d; flat %d ];' % (ac, touch, flat)

spellLevelGrammar = ( #{{{
'''
<ws> := [ \t]*
<nameChar> := [a-zA-Z/]+
<digits> := [0-9]*
name := nameChar+
level := digits+

caster := name, ws, level

>spellLevel< := caster, (',', ws, !, caster)*

spellLevelRoot := spellLevel
''') #}}}

class SpellLevelDispatcher(disp.DispatchProcessor):
    def spellLevel(self, t, buffer):
        return t[3]
    def caster(self, (t, s1, s2, sub), buffer):
        namePart, levelPart = sub
        name = disp.getString(namePart, buffer)
        level = int(disp.getString(levelPart, buffer))
        return name, level
    
spellLevelParser = parser.Parser(spellLevelGrammar, root='spellLevelRoot')

class Spell(Converter):

    def preamble(self):
        return [
            # don't know how to express this
            # ('', ns_rdf['title'], "DND3.5E monsters"),
            # ('', ns_rdf['comment'], "Exported from srd35.db"),
        ]

    def classes(self):
        return [
            (Literal('Spell'), ns_rdf['typeof'], ns_rdf["Class"]),
            (Literal("SpellDomain"), a, ns_rdf["Class"]),
            (Literal("MonsterousHumanoid"), a, Literal('SpellDomain'))
        ]

    def dump(self, f):
        assert self.alldata, ".load() not called"
        graph = ConjunctiveGraph()
        for triple in self.preamble():
            graph.add(triple)
        for triple in self.classes():
            graph.add(triple)
        for spell in self.alldata:
            for triple in spell:
                graph.add(triple)
        graph.serialize(destination=f, format='n3')
        graph.serialize(destination=sys.stdout, format='n3')

    def data(self, conn):
        c = conn.cursor()
        c.execute('''select 

name, altname, school, subschool, descriptor, spellcraft_dc, level, components,
casting_time, range, target, area, effect, duration, saving_throw,
spell_resistance, short_description, to_develop, material_components,
arcane_material_components, focus, description, xp_cost, arcane_focus,
wizard_focus, verbal_components, sorcerer_focus, bard_focus, cleric_focus,
druid_focus, full_text, reference

                from spell''')

        for (
                name, altname, school, subschool, descriptor, spellcraft_dc,
                level, components, casting_time, range, target, area, effect,
                duration, saving_throw, spell_resistance, short_description,
                to_develop, material_components, arcane_material_components,
                focus, description, xp_cost, arcane_focus, wizard_focus,
                verbal_components, sorcerer_focus, bard_focus, cleric_focus,
                druid_focus, full_text, reference
            ) in c:
            l = []
            n = lambda *t:l.append(t)
            spell = Literal(name)
            n(spell, a, ns_spell["Spell"])
            n(spell, ns_rdf['label'], Literal(name))
            n(spell, ns_spell['school'], Literal(school))
            if subschool:
                n(spell, ns_spell['subSchool'], Literal(subschool))
            for castertype, casterlevel in self.parseLevels(level):
                anon = BNode()
                n(spell, ns_spell['castBy'], anon)
                n(anon, ns_spell['casterType'], Literal(castertype))
                n(anon, ns_spell['casterLevel'], Literal(casterlevel))
            yield l

    def parseLevels(self, level):
        if not level:
            return []
        succ, children, end = spellLevelParser.parse(level, processor=SpellLevelDispatcher())        
        return children


if __name__ == '__main__':
    conn = sqlite3.connect('srd35.db')
    s = Skills()
    s.load(conn)
    s.dump(open('skill.n3', 'w'))

    s = Monsters()
    s.load(conn)
    s.dump(open('monster.n3', 'w'))

    s = Spell()
    s.load(conn)
    s.dump(open('spell.n3', 'w'))

    g = ConjunctiveGraph()
    g.load(file('skill.n3'), format='n3')
    g.load(file('monster.n3'), format='n3')
    g.load(file('spell.n3'), format='n3')
