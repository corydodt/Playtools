"""
Spell-Like Ability XML parser
"""
import sys
import re

from fudge import Fake

from pymeta.grammar import OMeta
from pymeta.runtime import ParseError

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
casterLevel  ::=  <caster> <t "level"> <spaces> <number>:d <letter>*  => [CL, d]
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
rdfaGrammar = """
node         ::=  :x  !(ww('NODE', x))
ws           ::=  :x  ?(isWS(x))           !(ww('WS', x))                              => x  
sepText      ::=  :x  ?(isSepText(x))           !(ww('SEPTEXT', x))                       => x

rdfaNode :name  ::=  :x ?(isProp(x, name))               !(ww('RDFANODE', name, x))                => x

spellName    ::=  <rdfaNode u"spellName">:x :content !(ww('SPELLNAME', x))         => x, content
plainQual    ::=  <rdfaNode u"qualifier">:x :content     !(ww('PLAINQUAL', x))                => x, content
casterLevel  ::=  <rdfaNode u"casterLevel">:x :content !(ww('CASTERLEVEL', x))         => x, content
dc           ::=  <rdfaNode u"dc">:x :content !(ww('DC', x))  => x, content
qual         ::=  <ws>?:ws (<plainQual>|<casterLevel>|<dc>):q   !(ww('QUAL', q)) => ws, q
spell        ::=  <sepText>*:crap <spellName>:s <qual>*:quals <ws>? <sep>:end  !(ww('SPELL', s))   => t.spell(crap, s, quals, end)

sep          ::=  <rdfaNode u"sep">:x                        !(ww('SEP', x))            => x
fStart       ::=  <rdfaNode u"frequencyStart">:x !(ww('FSTART', x))     => x
fGroup       ::=  <fStart>:start :frequency <spell>+:spells
                                                !(ww('FGROUP', [start, frequency, spells])) => t.fGroup(start, frequency, spells)

dcBasis      ::=  <rdfaNode u"saveDCBasis">:basis :content  => t.dcBasis(basis, content)
dcTopLevel   ::=  <rdfaNode u"dc">:dcTop :content  => t.dcTopLevel(dcTop, content)
clTopLevel   ::=  <casterLevel>:clTop => t.clTopLevel(*clTop)
remainderPfx ::=  <rdfaNode u"casterLevel">|<rdfaNode u"dcBasis">|<rdfaNode u"dcTopLevel">
unknownRemainder ::= (~<remainderPfx> <node>)*:x  !(ww('UR', x))  => x
remainderItem ::=  (<clTopLevel>|<dcBasis>|<dcTopLevel>):x  !(ww('REMI', x))  => x
beforeGroups ::=  (~<fStart> <node>)*:x !(ww('BEF', x))
groups       ::=   (<fGroup>:b1 <sepText>*:b2   => (b1,b2))+:b  !(ww('GROUPS', b)) => b
remainders   ::=  <remainderItem>:c1 (<sep>:s !(t.unparentNodes(s)) <sepText>* <remainderItem>)*:c !(c.insert(0, c1))  => c
sla          ::=  <beforeGroups> <groups> <remainders>:c  !(ww('SLA:C', c, ))
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
    def useNode(self, node):
        """
        Parse the xml and use it as the document for this tree
        """  
        self.node = node
        if hasattr(node, 'documentElement'):
            self.doc = node.documentElement.parentNode
        else:
            self.doc = node.ownerDocument

    def unparentNodes(self, *nodes):
        """
        For each node in nodes, remove it from its parent.
        """
        for n in nodes:
            n.parentNode.removeChild(n)

    def fGroup(self, start, frequency, spells, ):
        assert isProp(start, u'frequencyStart')
        freq = start.getAttribute('content')
        for crap, spell in spells:
            self.unparentNodes(spell)
        span = self.doc.createElement('span')
        span.setAttribute('p:property', 'frequencyGroup')
        span.setAttribute('content', freq)
        span.appendChild(frequency)
        for crap, spell in spells:
            span.appendChild(crap)
            span.appendChild(spell)
        util.substituteNodes(start, [span])
        return span

    def spell(self, crap, start, quals, end):
        spellName, _content = start
        assert isProp(spellName, u'spellName')
        assert isProp(end, u'sep')
        name = spellName.childNodes[0].data
        self.unparentNodes(end)
        span = self.doc.createElement(u'span')
        span.setAttribute(u'p:property', u'spell')
        span.setAttribute(u'content', name)
        pn = spellName.parentNode
        next = end.nextSibling
        span.appendChild(spellName)
        for ws, (q, _content) in quals:
            if ws:
                span.appendChild(ws)
            span.appendChild(q)
        if next:
            pn.insertBefore(next, span)
        else:
            pn.appendChild(span)

        if crap:
            r = ''
            for c in crap:
                r = r + c.data
                self.unparentNodes(c)
            crap = self.doc.createTextNode(u''.join(r))
        else:
            crap = self.doc.createTextNode(u'')
        return crap, span

    def clTopLevel(self, casterLevel, content):
        return casterLevel

    def dcTopLevel(self, dcTopLevel, content):
        return dcTopLevel

    def dcBasis(self, dcBasis, content):
        return dcBasis

def isWS(node, ):
    """
    Node is a textnode containing only whitespace
    """
    return node.nodeName == '#text' and node.data.strip() == ''

def isSepText(node, ):
    """
    Node is a textnode containing only whitespace or a separator
    """
    return node.nodeName == '#text' and node.data.strip() in ';,.'

def isProp(node, value):
    """
    Node has p:property set to value 
    """
    return hasattr(node, 'getAttribute') and node.getAttribute('p:property') == value


def debugWrite(*items):
    import inspect
    indent = ' ' * (len(inspect.stack()) - 34)
    print indent,
    r = []
    for a in items:
        if hasattr(a, 'nodeName') and a.nodeName == 'span':
            r.append('<%s>' % (a.getAttribute('p:property'),))
        else:
            r.append(str(a))
    print ' '.join(r)
    return 

def rdfaProcessSLAXML(node):
    """
    Given an SLA node that has been preprocessed, remove sep tags and freqStart
    tags, put in frequencies and spell wrappers.
    """
    globs = globals().copy()
    tree = NodeTree()
    tree.useNode(node)
    globs.update({'t':tree,
        'ww': lambda *x:None,
        # 'ww': debugWrite,
        })

    RDFaParser = OMeta.makeGrammar(rdfaGrammar, globs, 'RDFaParser')

    seq = flattenSLATree(tree.node)[1:]
    try:
        parser = RDFaParser(seq)
        parser.apply('sla')
    except ParseError:
        def propify(x):
            if hasattr(x, 'nodeName') and x.nodeName == 'span':
                if x.hasAttribute('p:property'):
                    return '<PROP {0}>'.format(x.getAttribute('p:property'))
            return x
        print map(propify, parser.input.data[:parser.input.position])
        print map(propify, parser.input.data[parser.input.position:])
        raise
    return tree.node

def processDocument(doc):
    """
    Fold, spindle and mutilate doc to get the necessary SLA structure.  Return the modified
    document.
    """
    slaNode = util.findNodeByAttribute(doc, u'topic', u'Spell-Like Abilities')
    if slaNode:
        pre = preprocessSLAXML(slaNode)
        outNode = rdfaProcessSLAXML(pre)

    return doc

