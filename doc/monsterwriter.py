from playtools.fact import systems
from playtools.util import rdfName

MONSTERS2 = systems['D20 SRD'].facts['monster2']

from xml.etree import ElementTree

uniqueMonster = set()
monsterMash = []

def pruneStatblock(x):
    """
    Remove a statblock from x, if any.  Modifies x in-place
    """
    statblock = x.find('*/table')
    if statblock is not None:
        if 'Hit Dice' in ElementTree.tostring(statblock):
            x.remove(statblock)


def o(s):
    """
    Correct this monster's HTML and index it
    """
    et = ElementTree.fromstring(s)
    pruneStatblock(et)

    # pull the rdfname off of the div, since it won't always match the monster
    # node it came from
    id = rdfName(et.attrib['topic'])
    et.attrib['id'] = id

    # TODO("""Find the topmost node containing text and make it an h2.  then
    # recursively find its children and make them h3, h4, ...""")


    # TODO("""What's going on with whales?  The statblock did not get
    # removed.""")

    # TODO("""Horses are also badly messed up""")

    # TODO("""Young adult red dragon skeleton statblock, cloud giant skeleton
    # statblock, advanced megaraptor, ettin, chimera, wolf, human warrior""")

    # TODO("""Gray render zombie, wyvern zombie, minotaur zombie, ogre zombie,
    # bugbear zombie, troglodyte zombie, human commoner zombie, kobold
    # zombie""")

    # TODO("""Colossus appears without a title""")

    s = ElementTree.tostring(et).decode('string-escape')
    if s not in uniqueMonster:
        uniqueMonster.add(s)
        monsterMash.append((id, s))

    return id

for m in MONSTERS2.dump():
    print m
    if m.fullText:
        id = o(m.fullText)
        # m.fullText = "http://goonmill.org/2009/monster.html#%s" % (id,)



fout = open('monsters2.html', 'w')
for _, monster in sorted(monsterMash):
    fout.write(monster)
