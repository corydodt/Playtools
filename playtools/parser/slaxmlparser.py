"""
Spell-Like Ability XML parser
"""
import re
from xml.dom import minidom

from fudge import Fake

from pymeta.grammar import OMeta

from playtools import util

PROP = u'http://goonmill.org/2007/property.n3#'


# fudge.Fake is handy for creating placeholder objects that repr() nicely
RAW = Fake("RAW")
FSTART = Fake("FSTART")
SEP  = Fake("SEP")
QUAL = Fake("QUAL")
DC = Fake("DC")
DCTOP = Fake("DCTOP")
DCBASIS = Fake("DCBASIS")
CL = Fake("CL")
CLTOP = Fake("CLTOP")


# {{{ preprocGrammar
preprocGrammar = """
t :x         ::=  <token x>
timeUnit     ::=  <t 'hour'>|<t 'round'>|<t 'day'>|<t 'week'>|<t 'month'>|<t 'year'>
fStartTime   ::=  <digit>+:d '/' <timeUnit>:t                       => ''.join(d+['/',t])
fStart       ::=  (<t 'Permanent'>|<t 'At will'>|<fStartTime>):f '-'  => A([FSTART, f])
sep          ::=  ('.'|';'|','):f                                   => A([SEP, f])
qual         ::=  '(' <qualInner> ')'
raw          ::=  <anything>:x                                      => A([RAW, x,])
slaText      ::=  (<fStart>|<qual>|<dcTopLevel>|<dcBasis>|<clTopLevel>|<sep>|<raw>)*

commaPar     ::=  ','|')'
number       ::=  <digit>+:d                                        => int(''.join(d))
caster       ::=  <t "caster">|<t "Caster">  
casterLevel  ::=  <caster> <t "level"> <spaces> <number>:d <letter>+  => [CL, d]
casterLevel  ::=  <caster> <t "level"> <t "equals"> (~<sep> <anything>)*:any  => [CL, "equals%s" % (''.join(any),)]
clTopLevel   ::=  <casterLevel>:cl                                  => A([CLTOP, cl[1]])
dc           ::=  <t "DC"> <spaces> <number>:d                      => [DC, d]
qualMisc     ::=  (~<commaPar> <anything>)*:x                       => ''.join(x).strip()
qualVanilla  ::=  <qualMisc>:x                                      => [QUAL, x]
qualAny      ::=  (<dc>|<casterLevel>|<qualVanilla>):x              => A(x)
qualInner    ::=  <qualAny> (',' <qualAny>)*

remMisc      ::=  (~<sep> <anything>)*:x                            => ''.join(x).strip()  
remVanilla   ::=  <remMisc>:x                                       => A([RAW, x])
statName     ::=  <t "Charisma">|<t "Dexterity">|<t "Constitution">|<t "Strength">|<t "Wisdom">|<t "Intelligence">
dcWords      ::=  <t "save">? (<t "DCs">|<t "DC">) (<t "is">|<t "are">)  
dcBasis      ::=  <t "The"> <dcWords> <statName>:s <t "-based">     => A([DCBASIS, s.lower()])
dcTopLevel   ::=  <t "save"> <t "DC"> <spaces> <number>:d
                               <t "+"> <t "spell"> <t "level">      => A([DCTOP, unicode(d) + " + spell level"])
dcTopLevel   ::=  <t "save"> <t "DC"> <spaces> <number>:d           => A([DCTOP, d])
remAny       ::=  (<dcTopLevel>|<clTopLevel>|<dcBasis>|<remVanilla>)
remainder    ::=  <remAny> (<sep> <remAny>)*
""" # }}}

# {{{ rdfaGrammar
## rdfaGrammar = """
## casterLevel  ::=  :x  ?(isProp(x, u"casterLevel"))
## dcBasis      ::=  :x  ?(isProp(x, u"dcBasis"))
## dcTopLevel   ::=  :x  ?(isProp(x, u"dcTopLevel"))
## fGroup       ::=  <fStart>:start <spell> (<sep> <spell>)* <sep>:end
## remainderItem ::=  <casterLevel>|<dcBasis>|<dcTopLevel>|<otherText>
## sla          ::=  <otherText>+ <ws>? <fGroup>+ <ws>? <remainderItem> (<ws>? <sep> <remainderItem>)*
## """
rdfaGrammar = """
node         ::=  :x  
ws           ::=  :x  ?(isWS(x))                                            => x  

spellName    ::=  :x  ?(isProp(x, u"spellName")) :content                   => x, content
plainQual    ::=  :x  ?(isProp(x, u"qualifier")) :content                   => x, content
casterLevel  ::=  :x  ?(isProp(x, u"casterLevel")) :content                 => x, content
dc           ::=  :x  ?(isProp(x, u"dc")) :content                          => x, content
qual         ::=  <ws>?:w (<plainQual>|<casterLevel>|<dc>):q                => w, q  
spell        ::=  <spellName>:s <qual>*:quals <ws>? <sep>:end               => t.spell(s, quals, end)

sep          ::=  :x  ?(isProp(x, u"sep"))                                  => x
fStart       ::=  :x  ?(isProp(x, u"frequencyStart"))                       => x
fGroup       ::=  <fStart>:start (~<sep> <anything>)*:any <sep>:end         => t.fGroup(start, any, end)

otherText    ::=  (~<sep> <node>)+ <sep>

sla          ::=  <otherText>+ <fGroup>+ <otherText>+
""" # }}}

def joinRaw(parsed):
    """
    Scan parsed for sequences of RAW characters, and put them back together as
    strings.  Leave alone other types of nodes.
    """
    out = []
    buffer = ''
    for type, data in parsed:
        if type is RAW:
            buffer += data
        else:
            if buffer:
                b = re.sub(r'\s+', ' ' , buffer)
                out.append((RAW, b))
                buffer = ''
            out.append((type,data))
    if buffer:
        b = re.sub(r'\s+', ' ' , buffer)
        out.append((RAW, b))
    return out

def skippableUp(node, check):
    """
    True, if node's parent is not already preprocessed
    """
    return node.parentNode.getAttribute('p:property') == check

def skippableLeft(node, check):
    """
    True, if node's previous sibling is not already preprocessed
    """
    if node.previousSibling:
        return node.previousSibling.getAttribute('p:property') == check

def substituteSLAText(orig, parsed):
    """
    Use parsed to construct a new sequence of nodes to put into parent
    """
    p = orig.parentNode
    doc = orig.ownerDocument
    substitutions = []
    for type, data in parsed:
        if type is RAW:
            substitutions.append(doc.createTextNode(data))
        elif type is DCBASIS:
            if not skippableUp(orig, 'dcBasis'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'saveDCBasis')
                span.setAttribute('content', data)
                tn = doc.createTextNode('The save DCs are ' + data.capitalize() + '-based')
                span.appendChild(tn)
                substitutions.append(span)
        elif type is QUAL:
            if not skippableUp(orig, 'qualifier'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'qualifier')
                tn = doc.createTextNode('(' + data + ')')
                span.appendChild(tn)
                substitutions.append(span)
        elif type is CLTOP:
            if not skippableUp(orig, 'casterLevel'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'casterLevel')
                span.setAttribute('content', unicode(data))
                tn = doc.createTextNode('Caster level %s' % (data,))
                span.appendChild(tn)
                substitutions.append(span)
        elif type is CL:
            if not skippableUp(orig, 'casterLevel'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'casterLevel')
                span.setAttribute('content', unicode(data))
                tn = doc.createTextNode('(caster level %s)' % (data,))
                span.appendChild(tn)
                substitutions.append(span)
        elif type is DCTOP:
            if not skippableUp(orig, 'dc'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'dc')
                span.setAttribute('content', unicode(data))
                tn = doc.createTextNode('save DC %s' % (data,))
                span.appendChild(tn)
                substitutions.append(span)
        elif type is DC:
            if not skippableUp(orig, 'dc'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'dc')
                span.setAttribute('content', unicode(data))
                tn = doc.createTextNode('(DC %s)' % (data,))
                span.appendChild(tn)
                substitutions.append(span)
        elif type is SEP:
            if not skippableLeft(orig, 'sep'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'sep')
                substitutions.extend([span, doc.createTextNode(data)])
            else:
                substitutions.extend([doc.createTextNode(data)])
        elif type is FSTART:
            if not skippableLeft(orig, 'frequencyStart'):
                span = doc.createElement('span')
                span.setAttribute('p:property', 'frequencyStart')
                span.setAttribute('content', data)
                substitutions.extend([span, doc.createTextNode(data + '-')])
            else:
                substitutions.extend([doc.createTextNode(data + '-')])
    util.substituteNodes(orig, substitutions)

def processDocument(doc):
    """
    Fold, spindle and mutilate doc to get the necessary SLA structure.  Return the modified
    document.
    """
    slaNode = util.findNodeByAttribute(doc, u'topic', u'Spell-Like Abilities')
    if slaNode:
        preprocessSLAXML(slaNode)

    return doc

def preprocessSLAXML(node):
    """
    Given that node is a DOM element containing spell-like ability descriptions, insert
    additional DOM nodes into the text where interesting properties are found.
    """
    node.ownerDocument.documentElement.setAttribute(u'xmlns:p', PROP)
    title = node.getElementsByTagName(u'b')[0]
    title.setAttribute(u'p:property', u'powerName')

    def addSpellNameRDFa(node):
        node.setAttribute(u'p:property', u'spellName')
        #

    spellNames = list( util.doNodes(node, lambda n: n.nodeName == 'i', addSpellNameRDFa) )
    assert len(spellNames) > 0

    globs = globals().copy()
    Preprocessor = OMeta.makeGrammar(preprocGrammar, globs, "Preprocessor")

    todo = node.childNodes[:]
    for n, cn in enumerate(todo):
        if cn.nodeName == 'p':
            todo[n+1:n+1] = cn.childNodes[:]
            continue
        if cn.nodeName == '#text':
            parsed = []
            globs['A'] = lambda *x: parsed.extend(x)
            Preprocessor(cn.data).apply('slaText')
            nodes = joinRaw(parsed)
            substituteSLAText(cn, nodes)

    return node

def flattenSLATree(node):
    """
    Return the child nodes under node as a sequence instead of a tree to make
    them easier to parse with a pattern matcher
    """
    todo = node.childNodes[:]
    for n, cn in enumerate(todo):
        todo[n+1:n+1] = cn.childNodes[:]
    return todo


class NodeTree(object):
    """
    A representation of the node tree that makes it easy to manipulate via the
    grammar
    """
    node = None
    def useXML(self, xml):
        """
        Parse the xml and use it as the document for this tree
        """  
        self.node = minidom.parseString(xml)

    def unparentNodes(self, *nodes):
        """
        For each node in nodes, remove it from its parent.
        """
        for n in nodes:
            n.parentNode.removeChild(n)

    def fGroup(self, start, rest, end):
        subs = []
        assert isProp(start, u'frequencyStart')
        assert isProp(end, u'sep')
        freq = start.getAttribute('content')
        self.unparentNodes(end, *rest)
        span = self.node.createElement('span')
        span.setAttribute('p:property', 'frequencyGroup')
        span.setAttribute('content', freq)
        for n in rest:
            span.appendChild(n)
        util.substituteNodes(start, [span])

    def spell(self, start, quals, end):
        subs = []
        spellName, _content = start
        assert isProp(spellName, u'spellName')
        assert isProp(end, u'sep')
        name = spellName.childNodes[0].data
        self.unparentNodes(end)
        span = self.node.createElement('span')
        span.setAttribute('p:property', 'spell')
        span.setAttribute('content', name)
        pn = spellName.parentNode
        next = end.nextSibling
        span.appendChild(spellName)
        for ws, (q, _content) in quals:
            span.appendChild(ws)
            span.appendChild(q)
        if next:
            pn.insertBefore(next, span)
        else:
            pn.appendChild(span)


def isWS(node, ):
    """
    Node is a textnode containing only whitespace
    """
    return node.nodeName == '#text' and node.data.strip() == ''

def isProp(node, value):
    """
    Node has p:property set to value 
    """
    return hasattr(node, 'getAttribute') and node.getAttribute('p:property') == value

def rdfaProcessSLAXML(xml):
    """
    Given an SLA node that has been preprocessed, remove sep tags and freqStart
    tags, put in frequencies and spell wrappers.
    """
    globs = globals().copy()
    tree = NodeTree()
    tree.useXML(xml)
    globs = {'t':tree}
    seq = flattenSLATree(tree.node)
    RDFaParser = OMeta.makeGrammar(rdfaGrammar, globs, 'RDFaParser')
    RDFaParser(seq).apply('sla')
    return tree.node
