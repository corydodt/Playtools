
from zope.interface import Interface

class ICharSheetSection(Interface):
    def asText(graph):
        pass

class IRuleFact(Interface):
    """
    A RuleFact is a certain kind of searchable, formattable object such as a
    Monster, Spell, Skill, Feat, Equipment, etc.  The domain of these things
    is an interface that allows use to index, look up, search for, and
    pretty-format them.
    """
