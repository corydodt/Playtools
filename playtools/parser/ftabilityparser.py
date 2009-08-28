"""
Parse the HTML of the full_text, extracting the description of the full abilities
"""

from xml.dom import minidom

from playtools.test.pttestutil import FIXME
from playtools.util import findNodes, doNodes, gatherText

def unescape(s):
    return s.replace(r'\n', '\n').replace(r'\"', '"')


def prepFT(s):
    return '<html>%s</html>' % (unescape(s),)


class Power(object):
    """
    A special ability power
    """
    nonPowers = []

    def __init__(self, name, useCategory, text):
        self.name = name
        self.useCategory = useCategory
        self.text = text

    @classmethod
    def fromNode(cls, node):
        """
        Create a Power from an ability node
        """
        nameN = node.getElementsByTagName('b')[0]
        nameN.parentNode.removeChild(nameN)
        try:
            name, catStuff = gatherText(nameN).rsplit(None, 1)
            cat = catStuff.rstrip(':')
            assert cat in '(Ex) (Su) (Sp)'.split()

            self = cls(name, cat[1:-1], node.toxml())
            return self
        except:
            cls.nonPowers.append(gatherText(nameN))

    @classmethod
    def fromSpellLike(cls, node):
        """
        Create a Power from a spell-like abilities node
        """
        nameN = node.getElementsByTagName('b')[0]
        nameN.parentNode.removeChild(nameN)
        self = cls('Spell-Like Abilities', 'Sp', node.toxml())
        return self


FIXME("findSpecialAbilities hardcodes level=8 which is probably wrong")
def findSpecialAbilities(combat):
    """
    Create Powers for each special ability found in the combat tag,
    excluding spell-like abilities.
    """
    def isAbility(node):
        """
        True if node is a special ability or set of spell-like abilities
        """
        if not hasattr(node, 'getAttribute'):
            return False

        topic = node.getAttribute('topic', )
        level = node.getAttribute('level', )
        return topic is not None and level=='8'

    def makePower(node):
        """
        Create a Power instance
        """
        topic = node.getAttribute('topic')
        if topic.lower() == 'spell-like abilities':
            power = Power.fromSpellLike(node)
            return power
        else:
            power = Power.fromNode(node)
            return power

    return list(doNodes(combat, isAbility, makePower))


def isCombatTag(node):
    """
    True if the node is the combat tag for the monster
    """
    return (hasattr(node, 'getAttribute') and 
            node.getAttribute('topic', ) == 'Combat')


def parseFTAbilities(s, prep=True):
    """
    Return a 2-tuple of (special abilities, spell-like abilities)
    """
    if prep:
        prepped = prepFT(s)
    else:
        prepped = s
    doc = minidom.parseString(prepped)

    combats = list(findNodes(doc, isCombatTag))
    if not combats:
        return []
    combat = combats[0]

    return findSpecialAbilities(combat)

