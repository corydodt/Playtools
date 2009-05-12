"""HyperEstraier-based indexing and searching """
# vi:ft=python
import sys, os
import shutil
import re

from twisted.web import microdom, domhelpers
from twisted.python import usage

import hypy

from playtools.util import RESOURCE


INDEX_DIRECTORY = RESOURCE('search-index')

slashRx = re.compile(r'\\([n"])')

def repSlash(m):
    if m.group(1) == 'n':
        return '\n'
    return m.group(1)

ALTRX = re.compile(r'[^a-zA-Z0-9\s]')


def makeAltName(s):
    """
    Normalize s to remove punctuation and case
    """
    s = ' '.join(s.strip().split())
    s = ALTRX.sub('', s).lower()
    return s


def indexItem(database, domain, item, quiet=False):
    """
    Take a row from an srd35 table and index it.  Assumes the table conforms
    to the norm of:
    .id - int id
    .name - string name
    .full_text - html text

    Add the domain to the attributes of the thing to help filter searches
    """
    _ft = re.sub(slashRx, repSlash, item.full_text)
    full = textFromHtml(_ft)
    doc = hypy.HDocument(uri=u'%s/%s' % (domain, unicode(item.id)))
    doc.addText(full)
    doc[u'@name'] = item.name
    doc[u'altname'] = makeAltName(item.name)
    doc[u'domain'] = domain
    # add item.name to the text so that it has extra weight in the
    # search results
    doc.addHiddenText(item.name)
    # pad with the altname so exact matches come up near the top
    doc.addHiddenText((doc[u'altname'] + " ") * 6)

    database.putDoc(doc, 0)

    if not quiet:
        sys.stdout.write(".")
        sys.stdout.flush()


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
    phrase = ' '.join(fuzzy)

    query = hypy.HCondition(phrase, matching='simple', max=max)
    query.addAttr(u'domain STREQ %s' % (domain,))

    r = estdb.search(query)

    return r


def buildIndex(estdb, domain, items, quiet=False):
    """
    Build an on-disk estraier index of all the items passed in; see
    textFromHtml for assumptions about the items.  Use the passed-in domain as
    the domain attribute.

    TODO: add a zope Interface to the classes of things that can be indexed,
    and adapt to that.
    """
    for n, item in enumerate(items):
        if n%100 == 0:
            if not quiet:
                sys.stdout.write("%s" % (n,))
            estdb.flush()
        indexItem(estdb, domain, item, quiet=quiet)


class Options(usage.Options):
    optParameters = [
            ['index-dir', None, INDEX_DIRECTORY, 'Where the index will be'],
            ['domain', None, u'monster', 'Domain (monster, spell, item...) to search inside of'],
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
        idir = self['index-dir']

        domain = self.decode(self['domain'])

        from playtools.query import db
        if self['build-index']:
            try:
                shutil.rmtree(idir)
            except EnvironmentError, e:
                pass

            estdb = hypy.HDatabase(autoflush=False)
            estdb.open(idir, 'a')
            buildIndex(estdb, u'spell', db.allSpells())
            buildIndex(estdb, u'monster', db.allMonsters())
            estdb.close()

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

