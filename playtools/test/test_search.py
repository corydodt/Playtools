"""
Test search functionality
"""
from __future__ import with_statement

import operator
import unittest
import re

from hypy import HDatabase, OpenFailed, CloseFailed

from .. import search, fact

from . import gameplugin, util


class SearchTest(unittest.TestCase):
    def setUp(self):
        self.index = HDatabase()

        with util.pluginsLoadedFromTest():
            systems = fact.getSystems()
            fact.importRuleCollections(systems)

        self.BADGERS = systems['Buildings & Badgers']

    def tearDown(self):
        try:
            self.index.close()
        except CloseFailed:
            pass

    def test_textFromHtml(self):
        """
        textFromHtml converts html into unicode text, and html with no text
        nodes into empty unicode strings
        """
        t = search.textFromHtml(u"<strong><div>hi<span>hello there</span></div> sup</strong")
        self.assertEqual(type(t), unicode)
        self.assertEqual(t, u"hi hello there  sup")

        # bad html with no text nodes
        t2 = search.textFromHtml(ur"<div topic=\"Heal, Mass\" level=\"5\"><p><")
        self.assertEqual(type(t2), unicode)
        self.assertEqual(t2, u"")

    def test_makeAltName(self):
        """
        makeAltName can convert title-cased text into altnames and handles
        punctuation appropriately
        """
        mk = search.makeAltName
        self.assertEqual(mk("hello"), "hello")
        self.assertEqual(mk("Hello"), "hello")
        self.assertEqual(mk("Hello There"), "hello there")
        self.assertEqual(mk("Cat's Grace"), "cats grace")
        self.assertEqual(mk("<Cat</>'s Grace"), "cats grace")
        self.assertEqual(mk("<Cat</>'s Grace, Mass"), "cats grace mass")

    def test_fuzzyQuoteTerm(self):
        """
        fuzzyQuoteTerm adds * appropriately and omits it for exact phrase
        searches
        """
        qt = search.fuzzyQuoteTerm
        self.assertEqual(qt("hi"), "hi*")
        self.assertEqual(qt("hi there"), "hi there")
        self.assertEqual(qt("cat's"), "cat's*")

    def test_indexItem(self):
        """
        indexItem indexes a single item which can be found, and make sure it's
        possible to search by altname
        """
        self.index.open(self.BADGERS.searchIndexPath, 'w')
        indexer = search.HypyIndexer(self.BADGERS.searchIndexPath)

        dbNinja = gameplugin.Badger(23, u'Ninja Badger', u"Hello<div>\\nmy pretty")

        indexer.indexItem(dbNinja, self.index, u'ninja')
        self.index.flush()

        self.assertEqual(len(self.index), 1)
        idxNinja = self.index[u'ninja/23']
        self.assertEqual(idxNinja.encode('ascii'), "Hello<div>\\nmy pretty")

        # altname will be "ninjas attack" - verify this is in the draft
        draft = str(idxNinja)
        self.assertTrue(re.search(r'\n\t.*ninja badger\n', draft), 
                "did not find 'ninja badger' in the draft document")

    def test_find(self):
        """
        After indexing a bunch of items, we can find them again in various
        ways, and max is respected
        """
        self.index.open(self.BADGERS.searchIndexPath, 'w')
        indexer = search.HypyIndexer(self.BADGERS.searchIndexPath)

        tests = [ # {{{
                (u"Hello<div>\\nmy pretty",                                        u"Ninja's Attack"),
                (ur"\n<div topic=\"Heal, Mass\" level=\"5\">heal mass<p><",        u"Heal, Mass"),
                (ur"\n<div topic=\"Hold Animal\" level=\"5\">hold animal<p>",      u"Hold Animal"),
                (ur"\n<div topic=\"Horrid Wilting\" level=\"5\">horrid wilting",   u"Horrid Wilting"),
                (ur"\n<div topic=\"Incendiary Cloud\" level=5>incendiary cloud",   u"Incendiary Cloud"),
                (ur"\n<div topic=\"Insanity\" level=\"5\"><p><h5>insanity ",       u"Insanity"),
                ] # }}}

        for n, (full_text, name) in enumerate(tests):
            thing = gameplugin.Badger(n, name, full_text)
            indexer.indexItem(thing, self.index, u'ninja')

        self.index.flush()

        f = lambda terms, max=10: search.find(self.index, u"ninja", terms, max)
        pluck = lambda things, attr: [x[attr] for x in things]

        self.assertEqual(pluck(f([u"ho"]), u"@uri"), [u'ninja/2', u'ninja/3'])
        self.assertEqual(pluck(f([u"ho"], max=1), u"@uri"), [u'ninja/2', ])
        self.assertEqual(pluck(f([u"insan"]), u"@uri"), [u'ninja/5'])
        self.assertEqual(pluck(f([u"ninjas attack"]), u"@uri"), [u'ninja/0'])

    def test_buildIndex(self):
        """
        An index can be built and it has spells and stuff in it.
        """
        _badgers = self.BADGERS.facts['badger']
        indexer = search.HypyIndexer(self.BADGERS.searchIndexPath)
        indexer.buildIndex(_badgers, beQuiet=True)

        self.index.open(self.BADGERS.searchIndexPath, 'r')
        self.assertEqual(len(self.index), 2)
        giantBadger = self.index[u'badger/73']
        self.assertEqual(giantBadger[u'altname'], "giant maneating badger")
