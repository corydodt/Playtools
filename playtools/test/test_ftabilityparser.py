"""
Test for the parsing of fulltext abilities.  These are the fulltext
descriptions of a monster's special abilities.
"""
import sys
import traceback
import inspect
from xml.dom import minidom

from twisted.trial import unittest

from playtools.parser import ftabilityparser as ft
from playtools import fact, util

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class FullTextAbilityParserTest(unittest.TestCase):
    """
    Test nuances of parsing
    """
    def test_thisLevel(self):
        """
        We can correctly identify the level of an sla node - whether the
        current node is inside a spell, inside a frequencyGroup or at the top
        level, outside all frequency groups.
        """
        s = inspect.cleandoc('''<div xmlns:p='http://' topic="Spell-Like Abilities" id="sla">
        <span id="1" />
        <span p:property="frequencyGroup" content="1/day" id="fg">
            <span id="2" />
            <span p:property="spell" id="sp">
                <span content="21" p:property="dc">(DC 21)</span><span content="10" p:property="casterLevel">(caster level 10)</span>
                <span id="3" />
            </span>
            <span p:property="spell">
                <span id="4" />
                <span p:property="qualifier">(this is it)</span>
                <span p:property="qualifier">(this is it too)</span>
            </span>
            <span content="19" p:property="dc">(DC 19)</span><span content="8" p:property="casterLevel">(caster level 8)</span>
        </span>
        <span content="charisma" p:property="saveDCBasis">The save DCs are Charisma-based</span>
        </div>''')
        n = minidom.parseString(s).documentElement
        t1 = util.findNodeByAttribute(n, 'id', '1')
        t2 = util.findNodeByAttribute(n, 'id', '2')
        t3 = util.findNodeByAttribute(n, 'id', '3')
        t4 = util.findNodeByAttribute(n, 'id', '4')
        tsla = util.findNodeByAttribute(n, 'id', 'sla')
        tfg = util.findNodeByAttribute(n, 'id', 'fg')
        tsp = util.findNodeByAttribute(n, 'id', 'sp')
        self.assertEqual(ft.thisLevelProperties(t1),
                {'basis': u'charisma',
                 'dc': None,
                 'casterLevel': None,
                 'frequency': None,
                 'qualifier': [],
                    })
        self.assertEqual(ft.thisLevelProperties(t2),
                {'basis': u'charisma',
                 'dc': u'19',
                 'casterLevel': u'8',
                 'frequency': u'1/day',
                 'qualifier': [],
                    })
        self.assertEqual(ft.thisLevelProperties(t3),
                {'basis': u'charisma',
                 'dc': u'21',
                 'casterLevel': u'10',
                 'frequency': u'1/day',
                 'qualifier': [],
                    })
        self.assertEqual(ft.thisLevelProperties(t4),
                {'basis': u'charisma',
                 'dc': u'19',
                 'casterLevel': u'8',
                 'frequency': u'1/day',
                 'qualifier': [u'(this is it)', u'(this is it too)'],
                    })
        self.assertEqual(ft.thisLevelProperties(tsla),
                {'basis': u'charisma',
                 'qualifier': [],
                 'dc': None,
                 'casterLevel': None,
                 'frequency': None,
                    })
        self.assertEqual(ft.thisLevelProperties(tfg),
                {'basis': u'charisma',
                 'dc': u'19',
                 'casterLevel': u'8',
                 'frequency': u'1/day',
                 'qualifier': [],
                    })
        self.assertEqual(ft.thisLevelProperties(tsp),
                {'basis': u'charisma',
                 'dc': u'21',
                 'casterLevel': u'10',
                 'frequency': u'1/day',
                 'qualifier': [],
                    })

    def test_null(self):
        """
        Monsters with no ft abilities parse as empty
        """
        self.assertEqual(ft.parseFTAbilities("<html />"), [])
        t2 = inspect.cleandoc("""<html>
            <head>
            <title>water mephit</title>
            </head>
            <body>
            <div id="waterMephit" level="3" topic="Water Mephit">
            <p/>
            <h3>Water Mephit</h3>
            <p>Water mephits speak Common and Aquan.</p>
            <div level="5" topic="Combat">
            <p/>
            <h5>Combat</h5>
            </div>
            </div>
            </body>
            </html>""")
        self.assertEqual(ft.parseFTAbilities(t2), [])

    def test_basic(self):
        """
        Simple special abilities can be found
        """
        t1 = inspect.cleandoc("""<html>
            <head>
            <title>water mephit</title>
            </head>
            <body>
            <div id="waterMephit" level="3" topic="Water Mephit">
            <p/>
            <h3>Water Mephit</h3>
            <p>Water mephits speak Common and Aquan.</p>
            <div level="5" topic="Combat">
            <p/>
            <h5>Combat</h5>
            <div level="8" topic="Breath Weapon">
            <p><b>Breath Weapon (Su):</b> 15-foot cone of caustic liquid, damage 1d8 acid, Reflex DC 13 half. The save DC is Constitution-based and includes a +1 racial bonus.</p>
            </div>
            </div>
            </div>
            </body>
            </html>""")
        actual = ft.parseFTAbilities(t1)
        self.assertEqual(map(repr, actual), 
                ["Power:Breath Weapon|Su|None|None|None|None|None"])

    def test_spellLike(self):
        t = inspect.cleandoc("""<div level="5" topic="Combat" xmlns:p="http://test">
            <p/>
            <h5>Combat</h5>
            <div level="8" topic="Spell-Like Abilities"> <p><b p:property="powerName">Spell-Like Abilities:</b> <span content="1/hour" p:property="frequencyGroup">1/hour-<span content="acid arrow" p:property="spell"><i p:property="spellName">acid arrow</i> <span p:property="qualifier">(can hurl an acidic
              blob that functions like the spell)</span> <span content="3" p:property="casterLevel">(caster level 3)</span></span></span>; <span content="1/day" p:property="frequencyGroup">1/day-<span content="stinking
                cloud" p:property="spell"><i p:property="spellName">stinking
                cloud</i> <span p:property="qualifier">(a mass of smelly fog that duplicates the effect of the spell)</span> <span content="15" p:property="dc">(DC 15)</span><span content="6" p:property="casterLevel">(caster level 6)</span></span></span>.<span content="charisma" p:property="saveDCBasis">The save DCs are Charisma-based</span>.</p> </div>
            </div>""")
        actual = ft.parseFTAbilities(t)
        self.assertEqual(map(repr, actual),
                ["Power:acid arrow|Sp|1/hour|charisma|None|3|"
                 "(can hurl an acidic blob that functions like the spell)",

                 "Power:stinking cloud|Sp|1/day|charisma|15|6|"
                 "(a mass of smelly fog that duplicates the effect of the spell)",
                 ])


class HUGEFullTextAbilityParserTest(unittest.TestCase):
    """
    Test every known Special stat against the parser
    """
    def test_huge(self):
        """
        Everything.
        """
        monsters = MONSTERS.dump()
        for monster in monsters:
            stat1 = monster.full_text

            try:
                if stat1:
                    act = [monster.name, ft.parseFTAbilities(stat1) and None]
            except:
                f = traceback.format_exc(sys.exc_info()[2])
                self.assertTrue(False,
                        "{x}\n{0}\n{1}\n".format(monster.name, stat1, x=f))
    test_huge.skip = "this test takes forever to run until i fix this stuff"

