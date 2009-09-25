"""
Utilities for unit tests
"""
from __future__ import with_statement

from itertools import chain, repeat, izip
try:
    from xml.etree import cElementTree as ET
    ET # for pyflakes
except ImportError:
    from xml.etree import ElementTree as ET

from rdflib.Graph import Graph
from rdflib import BNode
import re
import difflib
import operator
from pprint import pformat
from contextlib import contextmanager

from fudge.patcher import patched_context

from playtools.interfaces import IRuleSystem, IPublisher, IRuleCollection


# FIXME - not needed in python 2.6
def izip_longest(*args, **kwds):
    # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    fillvalue = kwds.get('fillvalue')
    def sentinel(counter = ([fillvalue]*(len(args)-1)).pop):
        yield counter()         # yields the fillvalue, or raises IndexError
    fillers = repeat(fillvalue)
    iters = [chain(it, sentinel(), fillers) for it in args]
    try:
        for tup in izip(*iters):
            yield tup
    except IndexError:
        pass


class DiffTestCaseMixin(object):
    """
    failIfDiff and failIfRxDiff powerup for xunit-compatible unit tests such
    as unittest and trial.
    """
    def getDiffMsg(self, first, second,
                     fromfile='First', tofile='Second'):
        """Return a unified diff between first and second."""
        # Force inputs to iterables for diffing.
        # use pformat instead of str or repr to output dicts and such
        # in a stable order for comparison.
        diff = difflib.unified_diff(
            first, second, fromfile=fromfile, tofile=tofile)
        # Add line endings.
        return '\n' + ''.join([d + '\n' for d in diff])

    def getFormattedVersions(self, first, second, formatter=None):
        if formatter is not None:
            return formatter(first, second)

        if isinstance(first, (tuple, list, dict)):
            first = [pformat(d) for d in first]
        else:
            first = [pformat(first)]

        if isinstance(second, (tuple, list, dict)):
            second = [pformat(d) for d in second]
        else:
            second = [pformat(second)]

        return first, second

    def failIfDiff(self, first, second, fromfile='First', tofile='Second',
            eq=operator.eq, formatter=None):
        """
        If not eq(first, second), fail with a unified diff.
        """
        if not eq(first, second):
            first, second = self.getFormattedVersions(first, second, formatter)

            msg = self.getDiffMsg(first, second, fromfile, tofile)
            raise self.failureException, msg

    assertNoDiff = failIfDiff

    def failIfRxDiff(self, first, second, fromfile='First', tofile='Second'):
        """
        Do the equality comparison using regular expression matching, using
        the first argument as the expression to match against the second
        expression.
        """
        assert type(first) is type(second) is list
        marks = {}

        # pad them
        ff = []
        ss = []
        for f, s in izip_longest(first, second, fillvalue='~~MISSING~~'):
            ff.append(f)
            ss.append(s)

        first = ff
        second = ss

        def eq(first, second):
            if len(first) != len(second):
                return False
            for n, (f, s) in enumerate(zip(first, second)):
                if re.match(f, s) is None:
                    marks[n] = f
            return len(marks) == 0

        def fmt(first, second, marks):
            l1 = []
            l2 = second
            for n, (f, s) in enumerate(zip(first, second)):
                if n not in marks:
                    l1.append(s)
                else:
                    l1.append(f)
            return l1, l2

        self.failIfDiff(first, second, fromfile, tofile, eq=eq,
                formatter=lambda ff, ss: fmt(ff, ss, marks)
                )

    assertNoRxDiff = failIfRxDiff


@contextmanager
def pluginsLoadedFromTest(mod):
    """
    Run code in a patched environment.  Utility function.  Pass in the module
    into you wish to patch getPluginsFake.
    """
    with patched_context(mod, "getPlugins", getPluginsFake):
        yield


def getPluginsFake(interface, mod):
    """
    Load a predetermined list of plugins from gameplugin.  Meant for use with 
    fudge.patcher.patch*
    """
    from playtools.test import gameplugin
    plugins = {IRuleSystem: [gameplugin.buildingsAndBadgers],
            IRuleCollection: [gameplugin.buildings, gameplugin.badgers],
            IPublisher: [gameplugin.htmlBuildingPublisher]
            }
    assert interface in plugins, "Modify getPluginsFake to support this new interface first"
    return iter(plugins[interface])


def pluck(items, *attrs):
    """
    For each item return getattr(item, attrs[0]) recursively down to the
    furthest-right attribute in attrs.
    """
    a = attrs[0]
    rest = attrs[1:]
    these = [getattr(o,a) for o in items]
    if len(rest) == 0:
        return these
    else:
        return pluck(these, *rest)


_signals = {}

def signal(which):
    def fn(s, details=None):
        """
        Spew a message to stderr to remind me to fix something
        """
        global _signals
        import traceback
        stack = traceback.extract_stack()
        f,l,fn = stack[-2][:3]
        if (f,l,fn) in _signals:
            return

        import sys, textwrap
        lines = [("%s: "%(which,)) + x for x in textwrap.wrap(s, 72)]
        print >>sys.stderr, '\n'.join(lines)
        print >>sys.stderr, '^^^^^ %s:%s:%s()' % (f,l,fn)
        _signals[(f,l,fn)] = s
    return fn

FIXME = signal('FIXME')
XXX = signal('XXX')
TODO = signal('TODO')

def padSeq(seq, padding):
    return chain(seq, repeat(padding))


def padZip(l1, l2, padding=None):
    """
    Return zip(l1, l2), but the shorter sequence will be padded to the length
    of the longer sequence by the padding
    """
    if len(l1) > len(l2):
        return zip(l1, padSeq(l2, padding))
    elif len(l1) < len(l2):
        return zip(padSeq(l1, padding), l2)

    return zip(l1, l2)


def formatFailMsg(seq, left="|| "):
    """Display the sequence of lines, with failure message"""
    ret = ['%r != %r\n']
    for s in seq:
        ret.append("%s%s\n" % (left, s))
    return ''.join(ret)


def compareElement(e1, e2):
    """Return None if they are identical, otherwise return the elements that differed"""
    if e1 is None or e2 is None:
        return e1, e2

    # compare attributes
    it1 = sorted(e1.items())
    it2 = sorted(e2.items())
    if it1 != it2:
        return e1, e2

    # compare text
    if e1.text != e2.text:
        return e1, e2

    # compare tail'd text
    if e1.tail != e2.tail:
        return e1, e2

    ch1 = e1.getchildren()
    ch2 = e2.getchildren()
    for c1, c2 in padZip(ch1, ch2):
        comparison = compareElement(c1, c2)
        if not comparison is None:
            return comparison

    return None


def compareXml(s1, s2):
    """
    Parse xml strings s1 and s2 and compare them
    """
    x1 = ET.fromstring(s1)
    x2 = ET.fromstring(s2)

    compared = compareElement(x1, x2)
    if compared is None:
        return True

    # TODO - return some information about the parts of the xml that differed
    return False


class IsomorphicTestableGraph(Graph):
    """
    Taken from http://www.w3.org/2001/sw/grddl

    Modified to ALSO test prefix identicality.
    """
    def __init__(self, **kargs): 
        super(IsomorphicTestableGraph,self).__init__(**kargs)
        self.hash = None
        
    def internal_hash(self):
        """
        This is defined instead of __hash__ to avoid a circular recursion scenario with the Memory
        store for rdflib which requires a hash lookup in order to return a generator of triples
        """ 
        return hash(tuple(sorted(self.hashtriples())))

    def hashtriples(self): 
        for triple in self: 
            g = ((isinstance(t,BNode) and self.vhash(t)) or t for t in triple)
            yield hash(tuple(g))

    def vhash(self, term, done=False): 
        return tuple(sorted(self.vhashtriples(term, done)))

    def vhashtriples(self, term, done): 
        for t in self: 
            if term in t: yield tuple(self.vhashtriple(t, term, done))

    def vhashtriple(self, triple, term, done): 
        for p in xrange(3): 
            if not isinstance(triple[p], BNode): yield triple[p]
            elif done or (triple[p] == term): yield p
            else: yield self.vhash(triple[p], done=True)
      
    def __eq__(self, G): 
        """Graph isomorphism testing."""
        if not isinstance(G, IsomorphicTestableGraph): 
            return False
        elif len(self) != len(G): 
            return False
        # check namespaces are bound to the same prefixes!
        elif sorted(self.namespaces()) != sorted(G.namespaces()): 
            return False
        elif list.__eq__(list(self),list(G)): 
            return True # @@
        return self.internal_hash() == G.internal_hash()

    def __ne__(self, G): 
       """Negative graph isomorphism testing."""
       return not self.__eq__(G)
