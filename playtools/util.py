import os

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
    return ''.join(parts)

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
