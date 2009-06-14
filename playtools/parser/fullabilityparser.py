"""
Parse the HTML of the full_text, extracting the description of the full abilities
"""

from xml.etree import ElementTree

def unescape(s):
    return s.replace(r'\n', '\n').replace(r'\"', '"')


def prepFullText(s):
    return '<html>%s</html>' % (unescape(s),)


def findCombatTag(tree):
    for combat in tree.getiterator():
        if combat.attrib.get('topic', None) == 'Combat':
            return combat
    else:
        return None


def findSpellLikeAbilities(combat):
    ret = []
    for i in combat.getiterator():
        topic = i.attrib.get('topic', None)
        if topic and topic.lower() == 'spell-like abilities':
            return i


def findSpecialAbilities(combat):
    """
    Return special abilities found in the Combat tag,
    excluding spell-like abilities.
    """
    ret = []
    for i in combat.getiterator():
        topic = i.attrib.get('topic', None)
        level = i.attrib.get('level', None)
        if topic is not None and level == '8':
            if topic.lower() == 'spell-like abilities':
                continue
            ret.append(i)

    return ret


def parseFullAbilities(s):
    """
    Return a 2-tuple of (special abilities, spell-like abilities)
    """
    prepped = prepFullText(s)
    combat = findCombatTag(ElementTree.fromstring(prepped))
    if combat is None:
        return (None, None)

    specAbs = findSpecialAbilities(combat)
    if specAbs is not None:
        specAbs = [ElementTree.tostring(e) for e in specAbs]

    spellLikes = findSpellLikeAbilities(combat)
    if spellLikes is not None:
        spellLikes = ElementTree.tostring(spellLikes)
 
    return (specAbs, spellLikes)

