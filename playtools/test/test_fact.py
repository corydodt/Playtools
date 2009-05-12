"""
Test the generalized fact layer
"""

from twisted.trial import unittest
from twisted.plugin import pluginPackagePaths

from playtools import fact, test

__all__ = []

class TestFactPluginLoading(unittest.TestCase):
    """
    Tests for the plugin-loading apparatus itself.
    """
    def setUp(self):
        """
        Provide our own PLUGINMODULE to playtools.fact and use that to test
        the functions that load our plugins.
        """
        pkg = test
        self.orig__path__ = pkg.__path__
        global __all__
        self.orig__all__ = __all__
        self.orig_PLUGINMODULE = fact.PLUGINMODULE
        pkg.__path__.extend(pluginPackagePaths(pkg.__name__))
        __all__ = []
        # monkeypatch fact so it loads plugins from our test directory
        fact.PLUGINMODULE = pkg

    def tearDown(self):
        fact.PLUGINMODULE = self.orig_PLUGINMODULE
        pkg = test
        pkg.__path__ = self.orig__path__
        global __all__
        __all__ = self.orig__all__

    def test_getSystems(self):
        """
        The getSystems function finds systems we have set up
        """
        systems = fact.getSystems()
        self.assertTrue('Buildings & Badgers' in systems)
        self.assertTrue(('Buildings & Badgers', '2.06') in systems)

    def test_importRuleCollections(self):
        from . import gameplugin
        badgers = gameplugin.BuildingsAndBadgersSystem()

        systems = {'Buildings & Badgers': badgers,
                ('Buildings & Badgers', '2.06'): badgers,
                }
        fact.importRuleCollections(systems)
        self.assertTrue('buildings' in badgers.facts)
        self.assertTrue('badgers' in badgers.facts)


class TestFact(unittest.TestCase):
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
        srd = ss[('D20 SRD', '3.5')]
        # verify that we can access by either name or name-version tuple
        self.assertIdentical(srd, ss['D20 SRD'])
        self.assertEqual(srd.__doc__.strip()[:50],
            'Game system based on the System Reference Document')
        self.assertEqual(srd.version, '3.5')

    def test_facts(self):
        """
        We can get a dict of fact domains that exist in a particular system
        """
        srd = fact.systems[('D20 SRD', '3.5')]
        pathfinder = fact.systems['Pathfinder']
        self.assertTrue('spell' in srd.facts)
        self.assertTrue('monster' in srd.facts)
        # test that fact collections are not inserted willy-nilly into random
        # systems
        self.assertFalse('spell' in pathfinder.facts)

    def test_dumpObject(self):
        """
        We can get a dump of all objects from a domain
        """
        srd = fact.systems[('D20 SRD', '3.5')]
        monsters = srd.facts['monster']
        dumped = monsters.dump()
        self.assertEqual(len(dumped), 681)
        self.assertEqual(dumped[0].name, u'Anaxim')

    def test_lookup(self):
        """
        For some domain, we can lookup an item in that domain
        """
        srd = fact.systems[('D20 SRD', '3.5')]
        monster = srd.facts['monster']
        self.assertEqual(monster.lookup(73).name, u'Three-Headed Sirrush')

    def test_getItem(self):
        """
        We can pull an item out of the collection by key
        """
        srd = fact.systems[('D20 SRD', '3.5')]
        monsters = srd.facts['monster']
        self.assertEqual(monsters[u'1'].name, u'Anaxim')
        self.assertEqual(monsters[u'Anaxim'].name, u'Anaxim')

