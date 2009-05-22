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

    def test_importDiceparser(self):
        import playtools.diceparser
        playtools.diceparser

    def test_importDice(self):
        import playtools.dice
        playtools.dice

    def test_importConvert(self):
        import playtools.convert
        playtools.convert

    def test_importSparqly(self):
        import playtools.sparqly
        playtools.sparqly

    def test_importUtil(self):
        import playtools.util
        playtools.util

    def test_importFact(self):
        import playtools.fact
        playtools.fact

    def test_importSearch(self):
        import playtools.search
        playtools.search

    def test_importPluginsCharsheet(self):
        import playtools.plugins.charsheet
        playtools.plugins.charsheet

    def test_importPluginsFeats(self):
        import playtools.plugins.feats
        playtools.plugins.feats

    def test_importPluginsMonsters(self):
        import playtools.plugins.monsters
        playtools.plugins.monsters

    def test_importPluginsSkills(self):
        import playtools.plugins.skills
        playtools.plugins.skills

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

