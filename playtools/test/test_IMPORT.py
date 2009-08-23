"""
Just import everything
"""

from twisted.trial import unittest

class IMPORTTestCase(unittest.TestCase):
    def test_importCharsheet(self):
        import playtools.charsheet
        playtools.charsheet

    def test_importCommon(self):
        import playtools.common
        playtools.common

    def test_importInterfaces(self):
        import playtools.interfaces
        playtools.interfaces

    def test_importDice(self):
        import playtools.dice
        playtools.dice

    def test_importConvert(self):
        import playtools.convert
        playtools.convert

    def test_importPublish(self):
        import playtools.publish
        playtools.publish

    def test_importPublisherplugin(self):
        import playtools.publisherplugin
        playtools.publisherplugin

    def test_importFact(self):
        import playtools.fact
        playtools.fact

    def test_importSearch(self):
        import playtools.search
        playtools.search

    def test_importSparqly(self):
        import playtools.sparqly
        playtools.sparqly

    def test_importUtil(self):
        import playtools.util
        playtools.util

    def test_importPluginsCharsheet(self):
        import playtools.plugins.charsheet
        playtools.plugins.charsheet

    def test_importPluginsMonstertext(self):
        import playtools.plugins.monstertext
        playtools.plugins.monstertext

    def test_importPluginsMonsters(self):
        import playtools.plugins.monsters
        playtools.plugins.monsters

    def test_importPluginsD20SRD35Config(self):
        import playtools.plugins.d20srd35config
        playtools.plugins.d20srd35config

    def test_importPluginsD20SRD35(self):
        import playtools.plugins.d20srd35
        playtools.plugins.d20srd35

    def test_importPluginsPathfinder10(self):
        import playtools.plugins.pathfinder10
        playtools.plugins.pathfinder10

    def test_importPluginsUtil(self):
        import playtools.plugins.util
        playtools.plugins.util

    def test_importParserAbilityparser(self):
        import playtools.parser.abilityparser
        playtools.parser.abilityparser

    def test_importParserAlignmentparser(self):
        import playtools.parser.alignmentparser
        playtools.parser.alignmentparser

    def test_importParserArmorclassparser(self):
        import playtools.parser.armorclassparser
        playtools.parser.armorclassparser

    def test_importParserAttackparser(self):
        import playtools.parser.attackparser
        playtools.parser.attackparser

    def test_importParserDiceparser(self):
        import playtools.parser.diceparser
        playtools.parser.diceparser

    def test_importParserFeatparser(self):
        import playtools.parser.featparser
        playtools.parser.featparser

    def test_importParserFtabilityparser(self):
        import playtools.parser.ftabilityparser
        playtools.parser.ftabilityparser

    def test_importParserMisc(self):
        import playtools.parser.misc
        playtools.parser.misc

    def test_importParserSaveparser(self):
        import playtools.parser.saveparser
        playtools.parser.saveparser

    def test_importParserSkillparser(self):
        import playtools.parser.skillparser
        playtools.parser.skillparser

    def test_importParserSpecialparser(self):
        import playtools.parser.specialparser
        playtools.parser.specialparser

    def test_importParserTreasureparser(self):
        import playtools.parser.treasureparser
        playtools.parser.treasureparser

    def test_importScriptsPtconvert(self):
        import playtools.scripts.ptconvert
        playtools.scripts.ptconvert

    def test_importScriptsPtstore(self):
        import playtools.scripts.ptconvert
        playtools.scripts.ptconvert

    def test_importScriptsPtsysteminstall(self):
        import playtools.scripts.ptconvert
        playtools.scripts.ptconvert

    def test_importScriptsRdftool(self):
        import playtools.scripts.ptconvert
        playtools.scripts.ptconvert

