"""
HyperEstraier-based indexing and searching
"""
import sys, os
import shutil
import re

from twisted.web import microdom, domhelpers
from twisted.python import usage

from playtools.interfaces import IIndexable, IRuleCollection

import hypy


ALTRX = re.compile(r'[^a-zA-Z0-9\s]')
def makeAltName(s):
    """
    Normalize s to remove punctuation and case
    """
    s = ' '.join(s.strip().split())
    s = ALTRX.sub('', s).lower()
    return s


def textFromHtml(htmlText):
    """
    Convert html text into its text nodes, with extreme leniency.  If the input
    is unicode, keep it unicode.
    """
    d = microdom.parseString(htmlText, beExtremelyLenient=1)
    s = domhelpers.gatherTextNodes(d, joinWith=u" ")
    ## print '\n'.join('| ' + l for l in s.splitlines())
    return s


ALWAYS_SKIP = object()

def fuzzyQuoteTerm(t):
    """Return a string term, quoted if a phrase, and with the fuzzy operator"""
    if ' ' in t:
        return t
    return '%s*' % (t,)


def find(estdb, domain, terms, max=10):
    """Use an estraier index to find monsters or other things"""
    fuzzy = [fuzzyQuoteTerm(t) for t in terms]
    phrase = u' '.join(fuzzy)

    query = hypy.HCondition(phrase, matching='simple', max=max)
    query.addAttr(u'domain STREQ %s' % (domain,))

    r = estdb.search(query)

    return r


class HypyIndexer(object):
    """
    Manager for Hypy HDatabases
    """
    def __init__(self, path):
        self.path = path

    def buildIndex(self, collection, beQuiet=False):
        """
        Extract the indexable text documents from the collection and index
        them under the named domain.

        TODO: add a zope Interface to the classes of things that can be indexed,
        and adapt to that.
        """
        assert IRuleCollection.providedBy(collection)

        estdb = hypy.HDatabase(autoflush=False)
        estdb.open(self.path, 'a')

        items = collection.dump()

        lastPct = 0
        for n, item in enumerate(items):
            pct = int(100.0*(float(n)/len(items)))
            if pct%10 == 0 and lastPct != pct:
                lastPct = pct
                if not beQuiet:
                    sys.stdout.write("%s%%" % (pct,))
                estdb.flush()
            self.indexItem(item, estdb, collection.factName, )
            if not beQuiet:
                sys.stdout.write(".")
                sys.stdout.flush()

        if not beQuiet:
            sys.stdout.write("100%")

    def indexItem(self, item, estdb, domain):
        """
        Add a single item to the Hypy index
        """
        item = IIndexable(item)

        full = item.text
        # TODO - this domain/uri is a little awkward if we ever use anything
        # other than a numeric id for URI. for example, this would not look
        # good: "spell/http://goonmill.org/2009/spells.n3#magicMissile"
        # Would rather have domain be <http://...spells.n3#> and uri be
        # <magicMissile>
        doc = hypy.HDocument(uri=u'%s/%s' % (domain, unicode(item.uri)))
        doc.addText(full)
        doc[u'@name'] = item.title
        doc[u'altname'] = makeAltName(item.title)
        doc[u'domain'] = domain.decode('ascii')
        # add item.title to the text so that it has extra weight in the
        # search results
        doc.addHiddenText(item.title)
        # pad with the altname so exact matches come up near the top
        doc.addHiddenText((doc[u'altname'] + " ") * 6)

        estdb.putDoc(doc, 0)


class Options(usage.Options):
    optParameters = [
            ['system', None, u'D20 SRD', 'Game system to search inside of, or index'],
            ['fact', None, u'monster', 'Fact Domain (monster, spell, item...) to search inside of'],
            ]
    optFlags = [
            ['build-index', 'b', 'Build a fresh index'],
            ['full-document', 'f', 'Display the entire document for each hit'],
            ]

    def decode(self, s):
        """
        Trying these encodings in order: [sys.stdin.encoding,
        sys.getdefaultencoding()], decode s and return a unicode.

        If s is already unicode, return s.
        """
        if type(s) is unicode: return s

        if sys.stdin.encoding:
            return s.decode(sys.stdin.encoding)

        # getdefaultencoding version
        return unicode(s)

    def parseArgs(self, *terms):
        self['terms'] = map(self.decode, terms)

    def postOptions(self):
        from playtools import fact  # import here to avoid circular import
                                    # while fact is loading its plugins (which
                                    # import from search, this module)

        system = fact.systems[self['system']]
        idir = system.searchIndexPath

        domain = self.decode(self['fact'])

        if self['build-index']:
            try:
                shutil.rmtree(idir)
            except EnvironmentError, e:
                pass

            system = fact.systems[self['system']]
            indexer = HypyIndexer(system.searchIndexPath)
            for collection in system.facts.values():
                indexer.buildIndex(collection)

        else:
            estdb = hypy.HDatabase(autoflush=False)
            estdb.open(idir, 'r')

            for hit in find(estdb, domain, self['terms']):
                print '<%s> %s' % (hit[u'@uri'], hit[u'@name'])
                if self['full-document']:
                    for line in hit.encode('utf-8').splitlines():
                        print '   ' + line
                print '    %s' % (hit.teaser(self['terms'], format='rst'),)


def run(argv=None):
    if argv is None:
        argv = sys.argv
    o = Options()
    try:
        o.parseOptions(argv[1:])
    except usage.UsageError, e:
        print str(o)
        print str(e)
        return 1

    return 0

if __name__ == '__main__': sys.exit(run())

