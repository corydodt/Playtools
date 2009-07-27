"""
Build a table of references
"""
import glob
import sys
from xml.dom import minidom

from playtools.util import rdfName, gatherText, findNodes

from urllib2 import urlopen, URLError

def verify():
    from playtools.fact import systems
    M = systems['D20 SRD'].facts['monster2']

    pool = Pool(processes=10)

    loaded = open('referencemap.txt')

    def checkPage(line):
        name, url = map(str.strip, line.split('\t'))
        kw = {'name':name, 'url':url}
        try:
            urlopen(url)
            print "OK: {name} {url}".format(kw)
            return (name,'ok')
        except URLError, e:
            kw['e'] = str(e)
            print "** ERROR: {name} {url} ({e:40})".format(kw)
            return (name,(url,e))


    # test 1: verify that every url we wrote is not 404
    checklist = pool.imap(checkPage, loaded, chunksize=3)
    checkdict = dict(checklist)

    # test 2: verify that every monster has a corresponding line in the file
    for m in sorted(M.dump(), key=lambda x:x.label):
        frag = m.resUri.partition('#')[-1]
        if frag not in checkdict:
            checkdict[frag] = (None, "not in referencemap.txt")

    # dump errors to stderr
    for k,v in sorted(checkdict.items()):
        if v != 'ok':
            print >>sys.stderr, k, v[1]

def run():
    fout = open('referencemap.txt', 'w')
    for f in glob.glob('srd/*.xml'):
        doc = minidom.parse(f)
        epic = False
        psionic = False

        alltext = gatherText(doc)
        if 'epic monsters' in alltext:
            epicPsionicOrNormal = 'epic/'
        elif 'psionic monsters' in alltext:
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
    run()
