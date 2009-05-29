"""
Utilities for easing the writing of tests.
"""
from __future__ import with_statement

import re
import difflib
import operator
from pprint import pformat
from contextlib import contextmanager

from fudge.patcher import patched_context

from itertools import repeat, chain, izip

import twisted.plugin

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
    these = (getattr(o,a) for o in items)
    if len(rest) == 0:
        return these
    else:
        return pluck(these, *rest)