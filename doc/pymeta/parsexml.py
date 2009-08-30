"""
Demonstration of some principles of parsing xml with ometa, and then parsing
text nodes in the same grammar.
"""
from pymeta.grammar import OMeta
from playtools.util import doNodes, gatherText
from xml.dom import minidom

gg = (r'''
textNode        ::= <token 'greater'> <spaces> <anything>*:foo !(''.join(foo)):bar  => bar
node            ::= ["#text" :attrs :node [ <textNode>:t ]]       => t
node            ::= [:name :attrs :node :cont]                    => []
contents        ::= <node>*:tree                                  => filter(None, tree)
''')

def doNodes(dom, matcher, cb=None):
    """
    Call cb(node) on every node under dom for which matcher(node) == True
    """
    todo = [dom]

    if cb is None:
        cb = lambda x: x

    for n, node in enumerate(todo):
        # slice assignment is fucking awesome
        todo[n+1:n+1] = list(node.childNodes)
        if matcher(node):
            yield cb(node)

def findNodes(dom, matcher):
    """
    Generate nodes matching the matcher function
    """
    for node in doNodes(dom, matcher):
        yield node

def gatherText(dom, accumulator=None):
    """
    Return all the text nodes
    """
    tn = findNodes(dom, lambda x: x.nodeName == '#text')
    return ' '.join([t.toxml() for t in tn])


def flatten(doc):
    everyNode = lambda x:True
    def _flatten(node):
        if node.nodeName == '#text':
            child = node.data
        elif len(node.childNodes) == 1 and node.childNodes[0].nodeName == '#text':
            child = node.childNodes[0].data
        else:
            child = node.childNodes
        return node.nodeName, node.attributes, node, child
    return doNodes(doc.documentElement, everyNode, _flatten)


G = OMeta.makeGrammar(gg, {'gatherText':gatherText, 'flatten':flatten})

test = '''<div level="8" topic="Spell-Like Abilities"> <p> At will- <i>animate dead</i>,  <i>blasphemy</i>,  <i>create greater undead</i>,  <i>create undead</i>,  <i>cone of cold</i>,  <i>desecrate</i>,  <i>greater dispel magic</i>,  <i>finger of death</i>,  <i>greater invisibility</i>,  <i>plane shift</i>,  <i>slay living</i>,  <i>speak with dead</i>,  <i>spectral hand</i>,  <i>greater teleport</i>,  <i>unholy aura</i>; 5/day- <i>haste</i>, <i>project image</i>,  <!-- comment for the hell of it --><i>weird</i>. Caster level 30th; save DC 26 + spell level.</p> <p>The save DCs are Charisma-based</p> </div>''' 
doc = minidom.parseString(test)
data = flatten(doc)

print G(data).apply('contents')

