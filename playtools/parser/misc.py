from playtools.test.util import TODO
from playtools.common import C

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


def parseAlignment(s):
    l = []
    punct = '()'
    for word in s.split():
        word = word.lower().strip(punct)
        if word == 'none':
            l.append(C.noAlignment)
            continue
        if word in ['always', 'often', 'usually']:
            l.append(getattr(C, 'aligned%s' % (word.capitalize())))
            continue
        if word in ['neutral', 'lawful', 'chaotic', 'evil', 'good']:
            l.append(getattr(C, word))
            continue

        if word in ['any']:    # this word is stupid and devoid of meaning
            continue

    if l:
        return l
    return [C.noAlignment]

"""bad alignments: {{{
Any (same as creator)
As master
Lawful evil or chaotic evil
Neutral evil or neutral
Often lawful good (normal); Usually lawful neutral or neutral (Deep)
Usually chaotic good (normal); Usually neutral (Wood)
Usually chaotic neutral, neutral evil, or chaotic evil
Usually neutral good or neutral evil
""" # }}}


def parseFamily(s):
    """
    Parse family, type and subtype (convert into a node)
    """
    TODO("""double blah, now we're importing fact in two different modules to hide
    it from the plugin system. move these parsers into other modules.""")
    from playtools import fact
    SRD = fact.systems['D20 SRD']
    knownFamilies = dict((unicode(x.label), x) for x in SRD.facts['family'].dump())
    import pdb; pdb.set_trace()


