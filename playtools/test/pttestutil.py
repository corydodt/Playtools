"""
Utilities for unit tests
"""
from itertools import chain, repeat
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET


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

def compareGraphs(g1, g2):
    """
    True if graphs g1 and g2 are the same graph
    """
    ns1 = sorted(g1.namespaces())
    ns2 = sorted(g2.namespaces())
    if ns1 != ns2:
        return False

    all1 = sorted(g1)
    all2 = sorted(g2)
    if all1 != all2:
        return False

    return True

