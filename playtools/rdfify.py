
import sqlite3
from rdflib import ConjunctiveGraph
import itertools

def rdfName(s):
    s = s.replace('-', ' ').replace("'", '')
    if s.count(',') == 1:
        first, last = s.split(',', 1)
        s = '%s %s' % (last, first)
    parts = s.split()
    parts[0] = parts[0].lower()
    parts[1:] = [p.capitalize() for p in parts[1:]]
    return ':' + ''.join(parts)

def rdfClass(s):
    return ':' + ''.join(p.capitalize() for p in s.split())

class Skills(object):
    def load(self, conn):
        self.alldata = list(self.data(conn))

    def dump(self, f):
        assert self.alldata, ".load() not called"
        for line in itertools.chain(self.preamble(), self.classes(), self.alldata):
            print >>f, line
            print line

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
                subtypes = " ".join('"%s"' % (st,) for st in subtype.split(","))
                yield '    :subType (%s);' % (subtypes,)
            yield '.'

        c.close()

class Monsters(Skills):

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
            yield '    p:treasure """%s""";' % (treasure,)
            # alignment

            # advancement
            # level_adjustment
            # special_abilities
            # stat_block

            # full_text
            # reference

            yield '.'


        c.close()

if __name__ == '__main__':
    conn = sqlite3.connect('srd35.db')
    s = Skills()
    s.load(conn)
    s.dump(open('skills.n3', 'w'))

    s = Monsters()
    s.load(conn)
    s.dump(open('monsters.n3', 'w'))

    g = ConjunctiveGraph()
    g.load(file('skills.n3'), format='n3')
    g.load(file('monsters.n3'), format='n3')
