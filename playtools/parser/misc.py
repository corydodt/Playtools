from playtools.test.util import TODO
from playtools.common import C
from playtools import fact

SRD = fact.systems['D20 SRD']
knownFamilies = dict((unicode(x.label), x) for x in SRD.facts['family'].dump())

def parseInitiative(s):
    """
    Some initiatives include explanations (show the math).  We consider these
    excess verbiage, and drop them.
    """
    splits = s.split(None, 1)
    if len(splits) == 1:
        return int(s)
    return int(splits[0])


def parseChallengeRating(s):
    if s.startswith('1/'):
        return [((1./int(s[2:])), None,)]
    else:
        try:
            return [(int(s), None)]
        except ValueError:
            items = map(unicode.strip, s.split(';', 1))
            l = []
            for i in items:
                parts = i.split(None, 1)
                if len(parts)>1:
                    l.append((int(parts[0]), parts[1]))
                else:
                    l.append((int(parts[0]), None))
            return l


def parseSize(s):
    s = s.lower()
    if s == 'colossal+':
        return C.colossalPlus
    return getattr(C, s.lower())


def parseFamily(s):
    """
    Parse family, type and subtype (convert into a node)
    """
    return knownFamilies.get(s, s)


def parseGrapple(s):
    """
    Integer-ize grapple numbers
    """
    if s in ['-', None]: return None
    s = s.split(None, 1)[0]
    return int(s)
