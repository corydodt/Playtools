import re
from xml.dom import minidom

from fudge import Fake

from pymeta.grammar import OMeta

from playtools.test.pttestutil import TODO

RAW = Fake("RAW")
FSTART = Fake("FSTART")
FEND = Fake("FEND")
QUAL = Fake("QUAL")

g = """
t :x      ::=   <token x>
fStartTime ::=  (<digit>+:d '/' (<t 'day'>|<t 'week'>):t)                    => ''.join(d+['/',t])
fStart    ::=   (<t 'At will'>|<fStartTime>):f '-'                           => (FSTART, f)
fEnd      ::=   ('.'|';'):f                                                  => (FEND, f)
qual      ::=   <exactly '('> (~<exactly ')'> <anything>)*:q <exactly ')'>   => (QUAL, ''.join(q))
raw       ::=   <anything>:x                                                 => (RAW, x,)  
slaText   ::=   (<qual>|<fStart>|<fEnd>|<raw>)*
"""

Frequelizer = OMeta.makeGrammar(g, globals(), "Frequelizer")

def reparseText(parsed):
    """
    Scan parsed for sequences of RAW characters, and put them back together as strings.
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

def substituteNodes(node, replacements):
    """
    Replace the node with a list of nodes that replace it
    """
    p = node.parentNode
    for r in replacements:
        p.insertBefore(r, node)
    p.removeChild(node)

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
        elif type is FEND:
            div = doc.createElement('div')
            div.setAttribute('p:property', 'frequencyEnd')
            substitutions.extend([div, doc.createTextNode(data)])
        elif type is FSTART:
            div = doc.createElement('div')
            div.setAttribute('p:property', 'frequencyStart')
            div.setAttribute('content', data)
            substitutions.extend([div, doc.createTextNode(data + '-')])
    substituteNodes(orig, substitutions)

def test1():
    test = """<div level="8" topic="Spell-Like Abilities" xmlns:p="http://goonmill.org/2007/property.n3#">
    <p><b p:property="powerName">Spell-Like Abilities:</b> At will-<i p:property="spellName">detect evil</i> (as a free action);
    3/day-<i p:property="spellName">cure light wounds</i> (Caster level 5th) (by touching a wounded creature with its horn); 
    1/day-<i p:property="spellName">cure moderate wounds</i> (Caster level 5th) (by touching a wounded creature with its horn), 
    <i p:property="spellName">neutralize poison</i> (DC 21, caster level 8th) (with a touch of its horn), 
    <i p:property="spellName">greater teleport</i> (anywhere within its home; it cannot teleport beyond the forest boundaries nor back from outside). The save DC is Charisma-based.</p>
    </div>"""

    doc = minidom.parseString(test)

    todo = doc.documentElement.childNodes[:]
    for n, cn in enumerate(todo):
        if cn.nodeName == 'p':
            todo[n+1:n+1] = cn.childNodes[:]
            continue
        if cn.nodeName == '#text':
            parsed = Frequelizer(cn.data).apply('slaText')
            nodes = reparseText(parsed)
            substituteSLAText(cn, nodes)

    print doc.toxml()

TODO("refine Frequelizer",
        """to also extract per-spell DC, overall caster level, and overall save DC basis""")


TODO("recursive descent SLA token finder",
        """use findnodes to return a flat list of all nodes which are frequencyStart,
        frequencyEnd, saveDC, qualifier, saveBasis, casterLevel, or spellName.
        """)

TODO("OMeta parser",
    """create a OMeta parser that takes the node tokens and produces a parsed SLA object
    """)

test1()
