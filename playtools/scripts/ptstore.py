"""
Tool to manipulate SQLite-backed triples databases. (library code)
"""

import warnings as w; w.filterwarnings('ignore')
import sys, os
import cmd
import pprint

from twisted.python import usage

from playtools.sparqly import (sqliteBackedGraph, filterNamespaces,
                TriplesDatabase)
from playtools.util import columnizeResult, prefixen


class Explorer(cmd.Cmd):
    prompt = 'ptstore> '
    intro = 'ptstore interactive - for exploring your stores\n'

    def __init__(self, store):
        cmd.Cmd.__init__(self)
        self.store = store
        self._quitting = False

    def do_id(self, arg):
        """Identify this store"""
        print self.store.graph.store.identifier, self.store.graph.default_context

    def do_quit(self, arg):
        """Quit"""
        self._quitting = True

    do_q = do_exit = do_quit

    def do_help(self, arg):
        """This help"""
        return cmd.Cmd.do_help(self, arg)

    def do_namespaces(self, arg):
        """Display our namespaces"""
        nss = sorted(list(self.store.graph.namespaces()))
        for pfx, uri in nss:
            print '@prefix %12s: <%s>.' % (pfx, uri)

    def postcmd(self, stop, line):
        return not not self._quitting

    def do_SELECT(self, arg):
        """Begin a SPARQL query"""
        try:
            res = self.store.query('SELECT ' + arg)
        except SyntaxError, e:
            print e
            print '** %s' % ('SELECT ' + arg, )
            return
        d = dict(self.store.graph.namespaces())
        print columnizeResult(res, d)

    do_select = do_SELECT
            

class OpenCommand(usage.Options):
    """
    Open and explore a store interactively: ptstore open <filename>
    """
    synopsis = "<filename>"

    def parseArgs(self, filename):
        self['filename'] = filename

    def postOptions(self):
        self.open()

    def open(self):
        tdb = TriplesDatabase()
        tdb.open(self['filename'])
        ex = Explorer(tdb)
        ex.cmdloop()


class CreateCommand(usage.Options):
    """
    Create a new database: ptstore create <filename>
    """
    synopsis = "<filename>"
    optFlags = [('force', 'f', "Wipe the db, if any, before creating"),
            ]

    def parseArgs(self, filename):
        self['filename'] = filename

    def postOptions(self):
        self.create()

    def create(self):
        filename = self['filename']
        if os.path.exists(filename):
            if self['force']:
                os.unlink(filename)
            else:
                raise usage.UsageError(
                        "** %s already exists, try ptstore create "
                        "--force to destroy it" % (filename,))

        path, filename = os.path.split(filename)
        self.graph = sqliteBackedGraph(path, filename)


class PullCommand(usage.Options):
    """
    Fill an existing database with data from a document at some URI
    """
    synopsis = "--n3 <uri> <filename>"
    optFlags = [
            ['verbose', 'v', 'Print more information (be verbose)'],
            ]
    optParameters = [['n3', None, None, 'Parse an N3 file from the given URI']
            ]
    n3list = None

    def opt_n3(self, uri):
        if self.n3list is None:
            self.n3list = []
        self.n3list.append(uri)

    def parseArgs(self, filename):
        self['filename'] = filename

    def postOptions(self):
        self.pull()

    def pull(self):
        filename = self['filename']
        if not os.path.exists(filename):
            raise usage.UsageError(
                    "** %s does not exist, try ptstore create first "
                    "or try a different filename." % (filename,))

        path, filename = os.path.split(filename)
        graph = self['graph'] = sqliteBackedGraph(path, filename)

        if self['verbose']:
            print 'Graph %s begins with %s triples' % (self['filename'],
                    len(graph))

        s1 = set(self.n3list)

        s2 = set(filterNamespaces(self.n3list))

        if self['verbose']:
            print 'Omitted some namespaces:\n %s' % ('\n '.join(list(s1-s2)),)

        for d in filterNamespaces(self.n3list):
            if self['verbose']:
                print 'Loading from %s' % (d,)
            graph.load(d, format='n3')

        graph.commit()

        # TODO - accept rdf etc. (--rdf <uri>)

        if self['verbose']:
            print 'Graph %s now contains %s triples' % (self['filename'],
                    len(graph))
        return graph


class Options(usage.Options):
    synopsis = "ptstore"

    subCommands = [
            ("create", None, CreateCommand, "Create a new store"),
            ("pull", None, PullCommand, "Read data from a URL and import it"),
            ("open", None, OpenCommand, "Open the store interactively"),
            ]

    # def parseArgs(self, ...):

    def postOptions(self):
        if self.subCommand is None:
            self.synopsis = "ptstore <subcommand>"
            raise usage.UsageError("** Please specify a subcommand (see \"Commands\").")


def run(argv=None):
    if argv is None:
        argv = sys.argv
    o = Options()
    try:
        o.parseOptions(argv[1:])
    except usage.UsageError, e:
        if hasattr(o, 'subOptions'):
            print str(o.subOptions)
        else:
            print str(o)
        print str(e)
        return 1

    return 0

