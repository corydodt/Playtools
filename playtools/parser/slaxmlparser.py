"""
Spell-Like Ability XML parser
"""
import re

from fudge import Fake

from pymeta.grammar import OMeta

from playtools.test.pttestutil import TODO
from playtools import util

PROP = u'http://goonmill.org/2007/property.n3#'


# fudge.Fake is handy for creating placeholder objects that repr() nicely
RAW = Fake("RAW")
FSTART = Fake("FSTART")
SEP  = Fake("SEP")
QUAL = Fake("QUAL")
DC = Fake("DC")
CL = Fake("CL")

# {{{ preprocGrammar
preprocGrammar = """
t :x         ::=  <token x>
fStartTime   ::=  (<digit>+:d '/' (<t 'day'>|<t 'week'>):t)         => ''.join(d+['/',t])
fStart       ::=  (<t 'At will'>|<fStartTime>):f '-'                => A([FSTART, f])
fEnd         ::=  ('.'|';'|','):f                                   => A([SEP, f])
qual         ::=  '(' <qualInner> ')'
raw          ::=  <anything>:x                                      => A([RAW, x,])
slaText      ::=  (<qual>|<fStart>|<fEnd>|<raw>)*

commaPar     ::=  ','|')'
number       ::=  <digit>+:d                                        => int(''.join(d))
casterLevel  ::=  <t "caster level"> <spaces> <number>:d <letter>+  => [CL, d]
dc           ::=  <t "DC"> <spaces> <number>:d                      => [DC, d]
qualMisc     ::=  (~<commaPar> <anything>)*:x                       => ''.join(x).strip()
vanilla      ::=  <qualMisc>:x                                      => [QUAL, x]
qualAny      ::=  (<dc>|<casterLevel>|<vanilla>):x                  => A(x)
qualInner    ::=  <qualAny> (',' <qualAny>)*
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
        elif type is QUAL:
            div = doc.createElement('div')
            div.setAttribute('p:property', 'qualifier')
            tn = doc.createTextNode('(' + data + ')')
            div.appendChild(tn)
            substitutions.append(div)
        elif type is SEP:
            div = doc.createElement('div')
            div.setAttribute('p:property', 'sep')
            substitutions.extend([div, doc.createTextNode(data)])
        elif type is FSTART:
            div = doc.createElement('div')
            div.setAttribute('p:property', 'frequencyStart')
            div.setAttribute('content', data)
            substitutions.extend([div, doc.createTextNode(data + '-')])
    util.substituteNodes(orig, substitutions)

def processDocument(doc):
    """
    Fold, spindle and mutilate doc to get the necessary SLA structure.  Return the modified
    document.
    """
    slaNode = util.findNodeByAttribute(doc, u'topic', u'Spell-Like Abilities')
    if slaNode:
        preprocessSLAXML(slaNode)

    assert len(frequencies) > 0
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
            def ex(*x):
                if None in x:
                    import pdb; pdb.set_trace()
                parsed.extend(x)
            globs['A'] = ex # lambda *x: parsed.extend(x)
            Preprocessor(cn.data).apply('slaText')
            nodes = joinRaw(parsed)
            substituteSLAText(cn, nodes)

    return node


if True: # {{{ TODOs
    TODO("refine Frequelizer",
            """to also extract per-spell DC, overall caster level, and overall save DC basis""")


    TODO("recursive descent SLA token finder",
            """use findnodes to return a flat list of all nodes which are frequencyStart,
            frequencyEnd, saveDC, qualifier, saveBasis, casterLevel, or spellName.
            """)

    TODO("OMeta parser",
        """create a OMeta parser that takes the node tokens and produces a parsed SLA object
        """)
    # }}}
