"""
Parse monster environments
"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers, chartypes
## appease pyflakes
numbers, chartypes

grammar = ( # {{{
r'''# environment stats
<ws>               :=  [ \t]*

<nonParen>         :=  letter/digit/whitespacechar/['"{}!@#*&^$%;:.,<>/?+-]

splat              :=  '*'  

qualifier          :=  '(', nonParen*, ')'

total              :=  digit+

environmentStat    :=  total, ws, math, ws, touch, ws, flatFooted
_environmentStat   :=  environmentStat
''') # }}}

environmentParser = parser.Parser(grammar, root="_environmentStat")


def parseEnvironment(s):
    """
    Parse environment
    """
    if s is None:
        s = "none"

    succ, children, end = environmentParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid environment expression' % (s,))
    return children


class Environment(object):
    """A fully parsed environment class
    """
    def __init__(self, name):
        self.value = None
        self.qualifier = None
        self.natural = None
        self.deflection = None
        self.otherInnate = None
        self.body = None
        self.shield = None


class Processor(disp.DispatchProcessor):
    def environmentStat(self, (t,s1,s2,sub), buffer):
        disp.dispatchList(self, sub, buffer)
        return self.environment

"""
Lillend	A chaos-aligned plane
Howler	A chaotic-aligned plane
Babau	A chaotic evil-aligned plane
Abyssal Greater Basi	A chaotic evil plane
Titan	A chaotic good-aligned plane
Celestial Charger, 7	A chaotic good plane
Nightmare	A evil-aligned plane
Leonal	A good-aligned plane.
Zelekhut	A lawful-aligned plane
Pit Fiend	A lawful evil-aligned plane
Nessian Warhound	A lawful evil plane
Trumpet Archon	A lawful good-aligned plane
Golden Protector (Ce	A lawful good plane
Nightmare, Cauchemar	A neutral evil plane
Yeth Hound	An evil-aligned plane
Xixecal	Any
Hoary Steed	Any cold
Treant, Elder	Any forest
Behemoth Eagle	Any forest, hill, mountains, and plains
Legendary Bear	Any forest, hill, mountains, plains, and underground
Legendary Tiger	Any forest, hill, mountains, plains, or underground
Angel, Solar	Any good-aligned plane
Water Elemental, Pri	Any land
Spectre	Any land and underground
Ghoul	Any\n(Lacedon: Any aquatic)
Prismasaurus	Any sunny land
Tayellah	Any temperate or cold land
Gloom	Any urban
Cerebrilith	Chaotic evil planes
Shark, Medium	Cold aquatic
Remorhaz	Cold desert
Wolverine	Cold forests
Ogre Mage	Cold hills
Gray Ooze	Cold marshes
White Dragon, Young	Cold mountains
Troll	Cold mountains\n(Scrag: Cold aquatic)
Frost Worm	Cold plains
Juvenile Arrowhawk	Elemental Plane of Air
Salt Mephit	Elemental Plane of Earth
Thoqqua	Elemental Plane of Fire
Water Mephit	Elemental Plane of Water
Xill	Ethereal Plane
Chaos Beast	Ever-Changing Chaos of Limbo
Shadow Mastiff	Plane of Shadow
Ravid	Positive Energy Plane
Ha-Naga	Temperate and warm land or underground
Triton	Temperate aquatic
Lammasu	Temperate deserts
Udoroot	Temperate forest
Elf, 1st-Level Warri	Temperate forest\n(Half-elf: Temperate forests)\n(Aquatic: Temperate aquatic)\n(Gray: Temperate mountains)\n(Wild: Warm forests)\n(Wood
Wolf	Temperate forests
Orc, 1st-Level Warri	Temperate hills
Gnome, 1st-Level War	Temperate hills (Forest gnomes: Temperate forests)
Ogre	Temperate hills (Merrow: Temperate aquatic)
Will-O'-Wisp	Temperate marshes
Twelve-Headed Hydra	Temperate marshes\n(Pyro: Warm marshes)\n(Cryo: Cold marshes)
Yrthak	Temperate mountains
Dwarf, 1st-Level War	Temperate mountains\n(Deep: Underground)
Worg	Temperate plains
Violet Fungus	Underground
Sahuagin	Warm aquatic
Half-Giant, 1st-Leve	Warm desert
Androsphinx	Warm deserts
Xeph, 1st-Level Warr	Warm forest
Behemoth Gorilla	Warm forest and warm mountains
Advanced Megaraptor	Warm forests
Wyvern Zombie	Warm hills
Stirge	Warm marshes
Young Adult Red Drag	Warm mountains
Tyrannosaurus	Warm plains
Halfling, 1st-Level	Warm plains\n(Deep halfling: Warm hills)\n(Tallfellow: Temperate forests)
"""
