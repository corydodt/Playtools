"""
Generally useful functions that don't relate to anything else in Playtools but
are used in Playtools.
"""
import os
import re

from twisted.python.util import sibpath

RESOURCE = lambda f: sibpath(__file__, f)

def rdfName(s):
    """Return a string suitable for an IRI from s"""
    s = s.replace('.', ' ')
    s = s.replace('-', ' ')
    s = s.replace("'", '')
    s = s.replace('/', ' ')
    s = s.replace(':', ' ')
    s = s.replace(',', ' ')
    s = s.replace('+', ' ')
    s = s.replace('(', ' ').replace(")", ' ')
    s = s.replace('[', ' ').replace("]", ' ')
    parts = s.split()
    parts[0] = parts[0].lower()
    parts[1:] = [p.capitalize() for p in parts[1:]]
    ret = ''.join(parts)
    if ret[0].isdigit(): ret = '_' + ret
    return ret

def filenameAsUri(fn):
    return 'file://' + os.path.abspath(fn)

def prefixen(prefixes, ref):
    """
    Return a shorter version of ref (as unicode) that replaces the long URI
    with a prefix in prefixes.  Or otherwise format it as a short unicode
    string.
    """
    # this path for formulae
    if hasattr(ref, 'namespaces'):
        return ref.n3()

    parts = ref.partition('#')
    doc = parts[0] + '#'
    for k,v in prefixes.items():
        if unicode(v) == doc:
            return '%s:%s' % (k, parts[2])
    return ref.n3()

def columnizeResult(res, prefixes=None):
    """
    Print a query result in nice columns
    """
    if prefixes is None:
        prefixes = {}
    ret = []
    for colName in res.selectionF:
        ret.append(colName[:26].ljust(28))
    ret.append('\n')
    px = lambda s: prefixen(prefixes, s)
    for item in res:
        for col in item:
            ret.append(px(col)[:26].ljust(28))
        ret.append('\n')
    return ''.join(ret)

def substituteNodes(node, replacements):
    """
    Replace the node with a list of nodes that replace it
    """
    p = node.parentNode
    for r in replacements:
        p.insertBefore(r, node)
    p.removeChild(node)

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

def flushLeft(text):
    """
    Reformat text without the leading whitespace.
    """
    m = re.search("(^\s*)", text)
    stripCount = len(m.group(1))
    ret = [l[stripCount:] for l in text.splitlines()]
    return '\n'.join(ret)

def findNodeByAttribute(root, attr, value):
    """
    Return the first node under root that has attr="value"
    """
    def matcher(n):
        if n.attributes:
            return n.getAttribute(attr) == value
    for n in findNodes(root, matcher):
        return n

