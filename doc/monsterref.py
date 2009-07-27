"""
Build a table of references
"""
import glob
import sys
from xml.dom import minidom
from urllib2 import urlopen, URLError

from playtools.util import rdfName, gatherText

class Checker(object):
    def __init__(self):
        self.cache = {}

    def doChecks(self):
        from playtools.fact import systems
        M = systems['D20 SRD'].facts['monster2']

        loaded = open('referencemap.txt')
        # dump errors to a log
        fout = open('referencemap.txt.log', 'w')

        # test 1: verify that every url we wrote is not 404
        for line in loaded:
            url, res = self.checkPage(line)
            if res != 'ok':
                fout.write("%s %s\n" % (url, res[1]))

        # test 2: verify that every monster has a corresponding line in the file
        for m in sorted(M.dump(), key=lambda x:x.label):
            frag = m.resUri.partition('#')[-1]
            if frag not in self.cache:
                self.cache[frag] = (None, "not in referencemap.txt")

    def checkPage(self, line):
        name, url = map(str.strip, line.split('\t'))
        kw = {'name':name, 'url':url}

        if url not in self.cache:
            try:
                urlopen(url)
                print "OK: {0[name]} {0[url]}".format(kw)
                self.cache[url] = 'ok'
            except URLError, e:
                kw['e'] = str(e)
                print "** ERROR: {0[name]} {0[url]} ({0[e]:40})".format(kw)
                self.cache[url] = (url, str(e))
        return url, self.cache[url]


def verify():
    checker = Checker()
    checker.doChecks()


def run():
    fout = open('referencemap.txt', 'w')
    for f in glob.glob('srd/*.xml'):
        doc = minidom.parse(f)

        alltext = gatherText(doc)
        if 'epic monsters' in alltext.lower():
            epicPsionicOrNormal = 'epic/'
        elif 'psionic monsters' in alltext.lower():
            epicPsionicOrNormal = 'psionic/'
        else:
            epicPsionicOrNormal = ''

        titlefrag = rdfName(gatherText(doc.getElementsByTagName('title')[0]))

        # build url 
        url = 'http://www.d20srd.org/srd/{epicPsionicOrNormal}monsters/{titlefrag}.htm'.format(
                epicPsionicOrNormal=epicPsionicOrNormal,
                titlefrag=titlefrag,
                )

        tables = doc.getElementsByTagName('table')
        statblocks = {}
        for t in tables:
            if 'full attack' in gatherText(t).lower():
                statblocks[t] = []
        assert statblocks != {}, f + " has no statblocks"
        
        # write one url per monster
        for sb in statblocks:
            # look in the top tr for the monsters' names
            tr = sb.getElementsByTagName('tr')[0]
            strongs = tr.getElementsByTagName('strong')
            assert len(strongs) > 0, "%s: %s has no monster names" % (f,
                    gatherText(tr)[:30])

            # convert each <strong> node into a monster's rdfName
            for strong in strongs:
                name = rdfName(gatherText(strong))
                fout.write("{rdfname}\t{url}\n".format(rdfname=name, url=url))


if __name__ == '__main__':
    ## run()
    verify()
