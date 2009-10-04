"""
Spell-Like Ability XML parser
"""
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


# define the actual grammar
preprocGrammar = open(util.RESOURCE('parser/slaxmlparser1.txt')).read()
rdfaGrammar = open(util.RESOURCE('parser/slaxmlparser2.txt')).read()

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

