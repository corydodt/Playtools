"""
Convert the d20 SRD SQLite database (library code)
"""

import sys

from twisted.python import usage

from playtools import convert


def getConverterSubcommands():
    """Return the 4-tuples of subcommands for all converters"""
    ret = []
    for c in convert.getConverters():
        ret.append((c.label(), None, c.commandLine, convert.converterDoc(c)))
    return ret


class Options(usage.Options):
    synopsis = """ptconvert [options] <converter> [<converter args>]""" 
    optFlags = [["quick", "q", "Just convert 10 items and stop"],
            ]
    subCommands = getConverterSubcommands()

    def postOptions(self):
        if self.subCommand is None:
            raise usage.UsageError("** You must specify the name of a converter!")
        c = convert.getConverter(self.subCommand)
        c.preamble()
        for n, item in enumerate(c):
            c.makePlaytoolsItem(item)
            if self['quick'] and n>=25:
                break

        io = sys.stdout
        c.writeAll(io)
        

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


