import re
from xml.dom import minidom

from fudge import Fake

from pymeta.grammar import OMeta

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
            parsed = reparseText(parsed)
            print parsed

test1()
