"""
Install the d20srd database
"""
import sys, os

from twisted.python import usage
from twisted.python.util import sibpath

from . import ptstore

from playtools.plugins.d20srd35config import SQLPATH, RDFPATH, SQLS, RDFURIS
from playtools import search, plugins

class Options(usage.Options):
    synopsis = "pt-system-install"

    def postOptions(self):
        self.install_rdf(RDFPATH)

        self.install_sql(SQLPATH)

        idx = self.create_index()

    def ptstore(self, *a):
        """
        Run ptstore with arguments
        """
        ptstore.run(['_ignored'] + list(a))

    def sqlite3(self, *a):
        """
        Run sqlite3 with arguments
        """
        quoted = ['"%s"'%x for x in a]
        os.system('sqlite3 %s' % (' '.join(quoted),))

    def install_rdf(self, path):
        """
        Create the RDF database by running ptstore pull
        """
        args1 = ['create', path]
        args2 = ['pull', '--verbose', path]
        uris = map(str.strip, RDFURIS)
        for uri in reversed(uris):
            args2[2:2] = ['--n3', uri]

        self.ptstore(*args1)

        self.ptstore(*args2)

    def install_sql(self, path):
        """
        Create the SQL database by running static SQL scripts
        """
        sqls = map(str.strip, SQLS)
        for f in sqls:
            f = sibpath(plugins.__file__, f)
            self.sqlite3('-init', f, path, '.exit')

        os.chmod(path, 0644)

    def create_index(self):
        search.run(['search.py', '--build-index'])


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


