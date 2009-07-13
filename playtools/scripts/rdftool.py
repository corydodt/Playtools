"""
Simple RDF/N3 conversion and testing tool
"""
import sys, os
import mimetypes

from twisted.python import usage

from rdflib import ConjunctiveGraph


class Options(usage.Options):
    synopsis = "rdftool [options] input-file"
    optParameters = [['outputFormat', 'O', 'n3', 'Output format to be written after conversion document'],
        ['inputFormat', 'I', 'by file extension; or n3', 'Format of the input document, if not guessed by filename'],
        ]

    def opt_inputFormat(self, format):
        self['inputFormatIsExplicit'] = True
        self['inputFormat'] = format

    def parseArgs(self, inputFile):
        if not os.access(inputFile, os.R_OK):
            raise usage.UsageError("** Cannot read %s: is it a real file?" % (inputFile,))
        self['inputFile'] = inputFile

    def postOptions(self):
        mimetypes.add_type('text/n3', '.n3')
        graph = ConjunctiveGraph()
        if self.get('inputFormatIsExplicit', False):
            fmt = self['inputFormat']
        else:
            mime, charset = mimetypes.guess_type(self['inputFile'])
            fmt = {'application/xml': 'xml', 
                   'application/rdf+xml': 'xml',
                   'text/n3': 'n3'}.get(mime, 'n3')

        graph.load(self['inputFile'], format=fmt)
        graph.serialize(destination=sys.stdout, format=self['outputFormat'])



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

