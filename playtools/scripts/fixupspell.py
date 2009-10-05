"""
fixupspell: add rdfa data tags to all the spell-like abilities and spells
inside playtools/plugins/monstertext/
"""

import sys
import shutil
import glob

from xml.dom import minidom
from xml.parsers.expat import ExpatError

from twisted.python import usage

from playtools.parser import slaxmlparser
from playtools import util
from playtools.test.pttestutil import TODO


class Options(usage.Options):
    synopsis = "fixupspell DIR"

    optParameters = [
        ['backup', 'i', '~', 'Suffix to save original filename as a backup']
        ]

    def parseArgs(self, dir):
        self['dir'] = dir

    def fixupFile(self, htm):
        try:
            doc = minidom.parse(open(htm))
        except ExpatError, e:
            raise usage.UsageError("** Could not parse {0}: {1}".format(htm, e)) 

        slaxmlparser.processDocument(doc)

        return doc

    def postOptions(self):
        TODO("print out all the raw text and qual text")
        for htm in sorted(glob.glob('{0}/*.htm'.format(self['dir']))):
            # FIXME
            print htm

            doc = self.fixupFile(htm)

            # FIXME
            if util.findNodeByAttribute(doc, 'topic', 'Spell-Like Abilities'):
                assert util.findNodeByAttribute(doc, 'p:property',
                        'frequencyGroup')

            if self['backup']:
                bak = '{0}{1}'.format(htm, self['backup'])
                shutil.copy(htm, bak)
            markup = doc.documentElement.toxml(encoding='utf-8')
            open('{0}'.format(htm), 'w').write(markup)


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

