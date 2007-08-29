
import sqlite3
from rdflib import ConjunctiveGraph
import itertools

def preamble():
    return [
        "@prefix : <http://thesoftworld/2007/skills.n3#>.",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        '@prefix c: <http://thesoftworld.com/2007/characteristic.n3#> .',
        '<> rdfs:title "DND3.5E skills" .',
        '<> rdfs:comment "Exported from srd35.db" .',
    ]

def classes():
    return [
        ":Skill a rdfs:Class .",
        ":SkillProperty a rdfs:Class .",
        ":TrainedSkill rdfs:subclassOf rdfs:Class .",
        ":UntrainedSkill rdfs:subclassOf rdfs:Class .",
        ":ArmorCheck rdfs:subclassOf rdfs:Class .",
        ":Psionic rdfs:subclassOf rdfs:Class .",
    ]

def data():
    conn = sqlite3.connect('srd35.db')
    c = conn.cursor()

    c.execute('''select name, subtype, key_ability, psionic, trained, armor_check, description, skill_check, action, try_again, special, restriction, synergy, epic_use, untrained, full_text, reference from skill''')

    def rdfName(s):
        parts = s.split()
        parts[0] = parts[0].lower()
        parts[1:] = [p.capitalize() for p in parts[1:]]
        return ':' + ''.join(parts)

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
            for st in subtype.split(','):
                yield '    :subType %s;' % rdfName(st)
        yield '.'

    c.close()
    conn.close()

if __name__ == '__main__':
    f = open('foo.n3', 'w')
    for line in itertools.chain(preamble(), classes(), data()):
        f.write(line)
        f.write('\n')
    f.close()

    g = ConjunctiveGraph()
    g.load(file('foo.n3'), format='n3')
