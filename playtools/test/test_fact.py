"""
Test the generalized fact layer
"""
from __future__ import with_statement

from twisted.trial import unittest

from playtools import fact
from playtools.test.pttestutil import pluginsLoadedFromTest

from . import gameplugin

__all__ = []

class TestFactPluginLoading(unittest.TestCase):
    """
    Tests for the plugin-loading apparatus itself.
    """
    def test_getSystems(self):
        """
        The getSystems function finds systems we have set up
        """
        with pluginsLoadedFromTest(fact):
            systems = fact.getSystems()

        self.assertTrue('Buildings & Badgers' in systems)
        self.assertTrue(('Buildings & Badgers', '2.06') in systems)

        badgers = systems[('Buildings & Badgers', '2.06')]
        # verify that we can access by either name or name-version tuple
        self.assertIdentical(badgers, systems['Buildings & Badgers'])
        self.assertEqual(badgers.__doc__.strip(),
            'The Buildings & Badgers role-playing game')
        self.assertEqual(badgers.version, '2.06')
        self.assertEqual(badgers.searchIndexPath, 'test-badgers-index')

    def _importRuleCollections(self, game):
        """
        Set up and run the importRuleCollections, which is boilerplate for
        several tests.
        """
        systems = {'Buildings & Badgers': game,
                ('Buildings & Badgers', '2.06'): game,
                }
        with pluginsLoadedFromTest(fact):
            fact.importRuleCollections(systems)

    def test_importRuleCollections(self):
        """
        Make sure importRuleCollections puts actual RuleCollections into the
        game systems
        """
        game = gameplugin.BuildingsAndBadgersSystem()
        self._importRuleCollections(game)
        self.assertTrue('building' in game.facts)
        self.assertTrue('badger' in game.facts)

    def test_lookup(self):
        """
        For some domain, we can lookup an item in that domain
        """
        game = gameplugin.BuildingsAndBadgersSystem()
        self._importRuleCollections(game)
        badgers = game.facts['badger']
        self.assertEqual(badgers.lookup(u'73').name, u'Giant Man-Eating Badger')

    def test_getitem(self):
        """
        We can pull an item out of the collection by key
        """
        game = gameplugin.BuildingsAndBadgersSystem()
        self._importRuleCollections(game)
        badgers = game.facts['badger']
        self.assertEqual(badgers[u'73'].name, u'Giant Man-Eating Badger')
        self.assertEqual(badgers[u'Giant Man-Eating Badger'].name, 
            u'Giant Man-Eating Badger')

    def test_dumpObject(self):
        """
        We can get a dump of all objects from a domain
        """
        game = gameplugin.BuildingsAndBadgersSystem()
        self._importRuleCollections(game)
        badgers = game.facts['badger']
        dumped = badgers.dump()
        self.assertEqual(len(dumped), 2)
        self.assertEqual(dumped[0].name, u'Small Badger')


class TestGameSystems(unittest.TestCase):
    """
    Tests for the plugins that get loaded by default
    """
    def test_systems(self):
        """
        We can get a dict of plugin systems with metadata
        """
        ss = fact.systems
        self.assertTrue(('Pathfinder', '1.0') in ss)
        self.assertTrue(('D20 SRD', '3.5') in ss)

    def test_facts(self):
        """
        We can get a dict of fact domains that exist in a particular system
        """
        srd = fact.systems['D20 SRD']
        pathfinder = fact.systems['Pathfinder']
        self.assertTrue('spell' in srd.facts)
        self.assertTrue('monster' in srd.facts)
        # test that fact collections are not inserted willy-nilly into random
        # systems
        self.assertFalse('spell' in pathfinder.facts)

