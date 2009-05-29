import os
import glob

import zc.buildout

from playtools.scripts import ptstore

from twisted.python.util import sibpath

class D20SRD35(object):
    """
    Do the work required to set up playtools' included D20 SRD 3.5e plugin.
    """
    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.options._buildout = buildout # wtf
        self.buildout = buildout

    def install(self):
        from playtools.plugins.d20srd35config import SQLPATH, RDFPATH

        self.install_rdf(RDFPATH)

        self.install_sql(SQLPATH)

        idx = self.create_index()

        return self.options.created()

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
        uris = map(str.strip, self.options['rdfURIs'].split())
        for uri in reversed(uris):
            args2[2:2] = ['--n3', uri]

        self.ptstore(*args1)
        self.options.created(path)

        self.ptstore(*args2)

    def install_sql(self, path):
        """
        Create the SQL database by running static SQL scripts
        """
        from playtools import plugins

        sqls = map(str.strip, self.options['sqls'].split())
        for f in sqls:
            f = sibpath(plugins.__file__, f)
            self.sqlite3('-init', f, path, '.exit')
            if path not in self.options.created():
                self.options.created(path)

        os.chmod(path, 0644)

    def create_index(self):
        from playtools import search, fact

        search.run(['search.py', '--build-index'])
        self.options.created(fact.systems['D20 SRD'].searchIndexPath)

    def update(self):
        """
        TODO - see if we can update create_index instead of reindexing every
        time.
        """
        1/0
