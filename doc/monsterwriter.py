import sys
import re

from playtools.fact import systems
from playtools.util import rdfName

MONSTERS2 = systems['D20 SRD'].facts['monster2']

from xml.dom import minidom

uniqueMonster = set()
monsterMash = []


def doNodes(dom, matcher, cb=None):
    """
    Call cb(node) on every node under dom for which matcher(node) == True
    """
    todo = [dom]

    for n, node in enumerate(todo):
        # slice assignment is fucking awesome
        todo[n+1:n+1] = list(node.childNodes)
        if matcher(node):
            cb(node)

def findNodes(dom, matcher):
    ret = []
    doNodes(dom, matcher, lambda x: ret.append(x))
    return ret

def gatherText(dom, accumulator=None):
    """
    Return all the text nodes
    """
    tn = findNodes(dom, lambda x: x.nodeName == '#text')
    return ' '.join([t.toxml() for t in tn])

REMSPACE = re.compile('\s+')
ALPHAONLY = re.compile('[[\]\\\'!"#$%&()*+,-./:;<=>?@_`{|}~^]')

def normalizeText(s):
    """
    Convert s by removing excess space and punctuation and case
    """
    s = s.lower()
    s = REMSPACE.sub(' ', s)
    s = ALPHAONLY.sub('', s)
    s = s.strip()
    return s


def hasAncestor(x, y):
    """
    True if y is an ancestor of x
    """
    while x.parentNode:
        x = x.parentNode
        if x is y:
            return True



class FullText(object):
    statblock = None
    apparentTitle = None

    def __init__(self):
        self.structure = []

    def __str__(self):
        ret = []
        todo = self.structure[:]
        REMOVE_PAREN = re.compile(r'\([^)]*\):?$')
        g = lambda x: normalizeText(REMOVE_PAREN.sub('', gatherText(x)))

        def walk(todo, indent=''):
            ret = []
            for xml, children in todo:
                if xml.nodeName == 'p':
                    ret.append('{brackets} _p_ {t}'.format(
                            brackets=indent,
                            t=g(xml)[:50],
                            ))
                elif xml.nodeName == 'table':
                    if xml is self.statblock:
                        ret.append('{brackets} [STATBLOCK] {t}'.format(
                            brackets=indent,
                            t=g(xml)[:50],
                            ))
                    else:
                        ret.append('{brackets} [T] {t}'.format(
                            brackets=indent,
                            t=g(xml)[:50],
                            ))
                else:
                    assert xml.hasAttribute('topic')
                    title = findNodes(xml, lambda zz: len(zz.childNodes) and
                            zz.childNodes[0].nodeName == '#text')[0]
                    topic = xml.getAttribute('topic')
                    gt = g(title)
                    if gt == normalizeText(topic):
                        actual = ''
                    else:
                        import pdb; pdb.set_trace()
                        actual = gt
                    ret.append('{brackets} {level}. {t} {_actual}'.format(
                        brackets=indent,
                        level=xml.getAttribute('level'), 
                        t=topic,
                        _actual=(
                            '!= {title}'.format(title=actual) if actual else '.')
                        )
                    )
                ret.extend(walk(children, indent + '>'))
            return ret

        lines = walk(self.structure[:])
        return '\n'.join(lines)

    @classmethod
    def byMapping(cls, xmlnode):
        """
        Constructor that finds notable structure
        """
        self = cls()

        self.statblock = findNodes(xmlnode, lambda x: x.nodeName == 'table' and 'Speed' in
                gatherText(x))[0]

        self.apparentTitle = gatherText(xmlnode.childNodes[0])

        def matcher(z):
            """
            True if z is a node with a topic, or a table
            """
            if hasattr(z, 'hasAttribute') and z.hasAttribute('topic'):
                return True
            if z.nodeName == 'table':
                return True
            if (z.nodeName == 'p' and 
                    z.parentNode is xmlnode and 
                    not z.parentNode.childNodes[0] is z and
                    gatherText(z).strip() != ''):
                return True
            return False


        def updateStructure(nodelist):
            """
            Build a nested structure by repeatedly calling gen.send(node), where each
            node is a div with a topic, and a list of other like divs that it contains.
            """
            nodeMap = {None: nodelist}
            while True:
                node = (yield)
                temp = node
                while True:
                    parent = temp.parentNode
                    if parent is temp.ownerDocument or parent is temp:
                        parent = None
                        break
                    if parent.hasAttribute('topic'):
                        break
                    temp = parent
                nodeMap[node] = []
                assert parent in nodeMap, "%s not in %s" % (
                        parent.getAttribute('topic'),
                        [(None if not hasattr(n, 'getAttribute') else
                            n.getAttribute('topic')) for n in nodeMap])
                nodeMap[parent].append([node, nodeMap[node]])
                
        updater = updateStructure(self.structure)
        updater.next()

        doNodes(xmlnode, matcher, updater.send)
        return self


def o(monster):
    """
    Correct this monster's HTML DOM
    """
    s = monster.fullText

    et = minidom.parseString(s).firstChild

    obj = FullText.byMapping(et)
    sb = obj.statblock
    sb.parentNode.removeChild(sb)

    # we will later use filterable to determine whether this block of text is
    # unique
    filterable = normalizeText(gatherText(et))

    # pull the rdfname off of the div, since it won't always match the monster
    # node it came from
    id = rdfName(et.getAttribute('topic'))
    et.setAttribute('id', id)
    
    if filterable not in uniqueMonster:
        uniqueMonster.add(filterable)
    else:
        return None, None

    # TODO("""Colossus, horses: missing titles""")
    xmltitle = normalizeText(obj.apparentTitle)
    monsterlabel = normalizeText(monster.label)
    if xmltitle not in monsterlabel and monsterlabel not in xmltitle:
        et.setAttribute("class", "badTitle")
        print >>sys.stderr, '!!!!!!!!!!!!!!!!!!!!!!!!!', obj.apparentTitle

    # TODO("""Find the topmost node containing text and make it an h2.  then
    # recursively find its children and make them h3, h4, ...""")

    print >>sys.stderr, str(obj)
    print >>sys.stderr, ''

    return id, et

def run(argv=None):
    fout = open('monsters2.html', 'w')
    fout.write("""<html><head><title>D20 SRD Monsters</title>
    <style type="text/css">.badTitle { background-color: yellow; }</style>
    </head><body>""")
    for m in sorted(MONSTERS2.dump(), key=lambda m:m.label):
        print
        print m
        if m.fullText:
            id, et = o(m)
            # m.fullText = "http://goonmill.org/2009/monster.html#%s" % (id,)
            if id:
                # done manipulating.  get the string.
                s = et.toxml('utf-8').decode('string-escape')
                fout.write(s)
    fout.write("""</body></html>""")


    ## for monster in sorted(monsterMash):

run()
