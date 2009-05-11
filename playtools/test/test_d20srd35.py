"""
We shall be able to pull facts about the srd35 system out using the API
"""

import unittest
from .. import fact
from playtools.plugins import d20srd35

class SRD35TestCase(unittest.TestCase):
    """
    Pull out the facts
    """
    def setUp(self):
        self.srd = fact.systems['D20 SRD']

    def test_lookup(self):
        """
        Spells and Monsters are available for lookup
        """
        srd = self.srd
        monsters = srd.facts['monster']
        spells = srd.facts['spell']

        def test(n,k,s):
            self.assertEqual(k.lookup(n).name, s)

        test(10, monsters, u'Behemoth Eagle')
        test(10, spells, u'Surelife')

    def test_thingLists(self):
        """
        Verify that we are retrieving the right number of things from the
        database with our dump methods

        Somewhat repeats the tests in test_fact in the absence of any other
        test fixture to test that.
        """
        srd = self.srd
        monsters = srd.facts['monster']
        spells = srd.facts['spell']
        mdump = monsters.dump()
        sdump = spells.dump()
        self.assertEqual(len(mdump), 681)
        self.assertEqual(len(sdump), 699)
        self.assertEqual(monsters[10].name, u'Behemoth Eagle')
        self.assertEqual(spells[10].name, u'Surelife')

    def test_srdReferenceURL(self):
        """
        The srdReferenceURL utility method returns a good URL into
        www.d20srd.org for a given item
        """
        srd = self.srd
        spells = srd.facts['spell']
        cswm = spells.lookup(205)
        self.assertEqual('http://www.d20srd.org/srd/spells/cureSeriousWoundsMass.htm',
                d20srd35.srdReferenceURL(cswm))
        animusBlast = spells.lookup(15)
        self.assertEqual('http://www.d20srd.org/srd/epic/spells/animusBlast.htm',
                d20srd35.srdReferenceURL(animusBlast))

