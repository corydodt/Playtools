"""
Just import everything
"""

from twisted.trial import unittest

class IMPORTTestCase(unittest.TestCase):
    def test_importCharsheet(self):
        import playtools.charsheet

    def test_importCommon(self):
        import playtools.common

    def test_importInterfaces(self):
        import playtools.interfaces

    def test_importDiceparser(self):
        import playtools.diceparser

    def test_importDice(self):
        import playtools.dice

    def test_importConvert(self):
        import playtools.convert

    def test_importSparqly(self):
        import playtools.sparqly

    def test_importUtil(self):
        import playtools.util

    def test_importFact(self):
        import playtools.fact

    def test_importSearch(self):
        import playtools.search

    def test_importPluginsCharsheet(self):
        import playtools.plugins.charsheet

    def test_importPluginsFeats(self):
        import playtools.plugins.feats

    def test_importPluginsMonsters(self):
        import playtools.plugins.monsters

    def test_importPluginsSkills(self):
        import playtools.plugins.skills

    def test_importPluginsD20SRD35Config(self):
        import playtools.plugins.d20srd35config

    def test_importPluginsD20SRD35(self):
        import playtools.plugins.d20srd35

    def test_importPluginsPathfinder10(self):
        import playtools.plugins.pathfinder10

    def test_importPluginsUtil(self):
        import playtools.plugins.util

