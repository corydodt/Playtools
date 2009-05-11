"""
Test the generalized fact layer
"""

from twisted.trial import unittest

from playtools import fact

class TestFact(unittest.TestCase):
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
        self.assertTrue('spell' in srd.facts)
        self.assertTrue('monster' in srd.facts)

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
