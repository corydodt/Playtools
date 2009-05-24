"""
Test the generalized domain formatter architecture
"""
from __future__ import with_statement

import string

from zope.interface import implements

from twisted.trial import unittest

from playtools import publish, fact
from playtools.test.util import pluginsLoadedFromTest
from playtools.test.gameplugin import buildings
from playtools.interfaces import IPublisher

class PublishTest(unittest.TestCase):
    def setUp(self):
        with pluginsLoadedFromTest():
            systems = fact.getSystems()
            self.bnb = systems['Buildings & Badgers']
            fact.importRuleCollections(systems)
            publish.publishers = publish.getPublishers()

    def test_getPublishers(self):
        """
        We can plug in a publisher by scanning for plugins.
        """
        self.assertTrue((self.bnb.name, buildings.factName, 'html') in publish.publishers)

    def test_customPublisher(self):
        """
        Can create a publication format and use it to publish an object
        """
        class LatexGenericPublisher(object):
            name = 'latex'
            def format(self, building, title=None):
                t = string.Template(r"""\documentclass[a4paper,12pt]{article}
\begin{document}
\section{$title}
$body
\end{document}
""")
                if title is None:
                    title = building.name
                r = t.substitute(title=title, body=building.full_text)
                return r
        #

        bldg = self.bnb.facts['building']
        badg = self.bnb.facts['badger']

        latexBuildingPublisher = LatexGenericPublisher()
        latexBuildingPublisher.collectionName = 'building'

        latexBadgerPublisher = LatexGenericPublisher()
        latexBadgerPublisher.collectionName = 'badger'

        # clone out the publisher registry so we can use it in other tests
        orig_registry = publish.publishers
        publish.publishers = publish.publishers.copy()
        try:
            publish.publishers[('Buildings & Badgers', 'building', 'latex')] = latexBuildingPublisher

            # 
            ret1 = publish.publish(bldg.lookup(u'2'), 'latex', title="badger house!")
            self.assertEqual(ret1, r"""\documentclass[a4paper,12pt]{article}
\begin{document}
\section{badger house!}
A castle (where badgers live)
\end{document}
""")

            # when the publisher is NOT registered for a particular fact, we raise
            # an exception
            nasty = badg.lookup(u'73')
            self.assertRaises(KeyError, lambda *a: publish.publish(nasty, 'latex'))

            # now register it and see it work
            publish.publishers[('Buildings & Badgers', 'badger', 'latex')] = latexBadgerPublisher
            ret2 = publish.publish(badg.lookup(u'73'), 'latex')
            self.assertEqual(ret2, r"""\documentclass[a4paper,12pt]{article}
\begin{document}
\section{Giant Man-Eating Badger}
Giant, hideous, bad-tempered space badger.
\end{document}
""")
        finally:
            publish.publishers = orig_registry
        #

    def test_publish(self):
        """
        Can format as one of the known formats, and pass in kw to format
        """
        bldg = self.bnb.facts['building']
        ret = publish.publish(bldg.lookup(u'2'), 'html', title="hello kitty")
        self.assertEqual(ret, """<html><head>
<title>hello kitty</title>
</head>
<body>
<h1>hello kitty</h1>
A castle (where badgers live)
</body>
</html>
""")
    #

    def test_override(self):
        """
        We can install a custom formatter that overrides an existing one
        """
        class HTMLBuildingPublisher2(publish.PublisherPlugin):
            implements(IPublisher)
            name = 'html'
            def format(self, building, title=None, app=None):
                t = string.Template(r"""<html><head>
<title>$title - Goonmill</title>
</head>
<body>
<h1>$title</h1>
$body
$app
</body>
</html>
""")
                if title is None:
                    title = building.name
                if app is None:
                    app = u''
                r = t.substitute(title=title, body=building.full_text, app=app)
                return r
        #

        bldg = self.bnb.facts['building']

        htmlBuildingPublisher2 = HTMLBuildingPublisher2(self.bnb.name,
                bldg.factName)

        publish.override(bldg, htmlBuildingPublisher2)

        ret = publish.publish(bldg.lookup(u'2'), 'html', app="Goonmill")
        self.assertEqual(ret, """<html><head>
<title>Castle - Goonmill</title>
</head>
<body>
<h1>Castle</h1>
A castle (where badgers live)
Goonmill
</body>
</html>
""")
        #

