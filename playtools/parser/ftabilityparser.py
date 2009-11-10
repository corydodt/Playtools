"""
Parse the HTML of the full_text, extracting the description of the full abilities
"""
import re
from xml.dom import minidom

from playtools import util

def unescape(s):
    return s.replace(r'\n', '\n').replace(r'\"', '"')


def prepFT(s):
    return '<html>%s</html>' % (unescape(s),)


class Power(object):
    """
    A special ability power
    """
    powerCount = 0
    parsedBySLAXML = False # set to true if this came out of the slaxmlparser
    nonPowerCount = 0
    nonPowers = []
    useCategory = None
    frequency = None
    basis = None
    dc = None
    casterLevel = None
    qualifier = None

    def __repr__(self):
        return ("Power:{0.name}|{0.useCategory}|{0.frequency}|{0.basis}|"
                "{0.dc}|{0.casterLevel}|{0.qualifier}".format(self))

    def __init__(self, name, useCategory, text):
        self.name = name
        self.useCategory = useCategory
        self.text = text

    @classmethod
    def fromNode(cls, node):
        """
        Create a Power from an ability node
        """
        nameN = node.getElementsByTagName('b')[0]
        nameN.parentNode.removeChild(nameN)
        try:
            name, catStuff = util.gatherText(nameN).rsplit(None, 1)
            cat = catStuff.rstrip(':')
            assert cat in '(Ex) (Su) (Sp)'.split()

            self = cls(name, cat[1:-1], node.toxml())
            cls.powerCount = cls.powerCount + 1
            return self
        except:
            t = util.gatherText(nameN)
            if t not in ['Carrying Capacity:',
                    'Abomination Traits:', 'Construct Traits:', 
                    'Undead Traits:', 'Ooze Traits:', 'Swarm Traits:', 
                    'Vermin Traits:', 'Plant Traits:', 'Cold Subtype:', 
                    'Incorporeal Traits:', 'Possessions:', 
                    'Elf Traits:', 'Challenge Rating:', 'Feats:', 
                    'Fire Subtype:', 'Immunities:', 'Outsider Traits:',
                    'Resistances:',
                    ]:
                cls.nonPowers.append(t)

    @classmethod
    def fromSpellLike(cls, node):
        """
        Create a Power from a spell-like abilities node
        """
        fgroups = util.findNodesByAttribute(node, 'p:property', 'frequencyGroup')
        powers = []
        for group in fgroups:
            spells = util.findNodesByAttribute(group, 'p:property', 'spell')
            for spell in spells:
                name = spell.getAttribute('content')
                props = thisLevelProperties(spell)
                pow = cls(re.sub(r'\s+', ' ', name), u'Sp', u'')
                pow.parsedBySLAXML = True
                pow.frequency = props['frequency']
                pow.basis = props['basis']
                pow.dc = props['dc']
                pow.casterLevel = props['casterLevel']
                pow.qualifier = re.sub(r'\s+', ' ', ' '.join(props['qualifier']))
                powers.append(pow)

        return powers


def thisLevelProperties(node):
    """
    Pull out dc, basis, casterLevel, other props for any powers in the same
    level as the current node
    """
    # find the nearest container, upwards
    while node:
        top = node
        if util.attr(top, 'p:property', 'frequencyGroup'
                ) or util.attr(node, 'p:property', 'spell'
                ) or (util.attr(node, 'topic') and
                        node.getAttribute('topic') in 
                            ['Spell-Like Abilities', 'Other Spell-Like Abilities']):
            break
        node = node.parentNode

    skip = list(util.findNodesByAttribute(top, 'p:property', 'frequencyGroup'))
    skip = skip + list(util.findNodesByAttribute(top, 'p:property', 'spell'))

    if top in skip:
        skip.remove(top)

    # find all properties, downwards from the container
    props = {'frequency': None,
            'basis': None,
            'dc': None,
            'casterLevel': None,
            'qualifier': []
            }
    todo = [top]
    for n, node in enumerate(todo):
        if node in skip:
            continue
        if util.attr(node, 'p:property'):
            if node.getAttribute('p:property') == 'frequencyGroup':
                props['frequency'] = node.getAttribute('content')
            elif node.getAttribute('p:property') == 'saveDCBasis':
                props['basis'] = node.getAttribute('content')
            elif node.getAttribute('p:property') == 'casterLevel':
                props['casterLevel'] = node.getAttribute('content')
            elif node.getAttribute('p:property') == 'dc':
                props['dc'] = node.getAttribute('content')
            elif node.getAttribute('p:property') == 'qualifier':
                props['qualifier'].append(util.gatherText(node))
        todo[n+1:n+1] = node.childNodes[:]

    # find missing properties, upwards from the container
    unfilled = dict([x for x in props.items() if x[1] is None])
    if unfilled and top.parentNode:
        rest = thisLevelProperties(top.parentNode)
        for k,v in rest.items():
            if props[k] is None:
                props[k] = v

    return props

def parseFTAbilities(s, prep=True):
    """
    Return a list of special abilities
    """
    if prep:
        prepped = prepFT(s)
    else:
        prepped = s

    if not s:
        return []

    doc = minidom.parseString(prepped)

    combat = util.findNodeByAttribute(doc, 'topic', 'Combat')
    if combat is None:
        return []

    levelNodes = util.findNodesByAttribute(combat, 'level')
    levelNodes.next() # skip over the combat node itself
    powers = []
    for node in levelNodes:
        topic = node.getAttribute('topic').lower() 
        if topic in ['spell-like abilities', 'other spell-like abilities']:
            powers.extend(Power.fromSpellLike(node))
        elif node.getAttribute('topic').lower() == 'skills':
            continue
        else:
            p = Power.fromNode(node)
            if p is not None:
                powers.append(p)

    return powers

