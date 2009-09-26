"""
test_slaxmlparser verifies the processes that convert XML nodes containing spell-like abilities
into formed XML structures.
"""
import inspect
from xml.dom import minidom

from twisted.trial import unittest

from playtools.parser import slaxmlparser as sxp
from playtools.test.pttestutil import DiffTestCaseMixin

class QualTest(unittest.TestCase, DiffTestCaseMixin):
    """
    Test the parsing of quals
    """
    def setUp(self):
        globs = {'QUAL': sxp.QUAL, 'DC': sxp.DC, 'CL': sxp.CL}
        self.parsed = []
        globs['A'] = lambda *x: self.parsed.extend(x)
        self.parser = sxp.OMeta.makeGrammar(sxp.preprocGrammar, globs, "Preprocessor")

    def test_DC(self):
        """
        Quals containing DC get parsed
        """
        self.parser("DC 21").apply("qualInner")
        expected = [[sxp.DC, 21]]
        self.assertEqual(self.parsed, expected)

        self.parsed = []
        self.parser("DC x21").apply("qualInner")
        expected = [[sxp.QUAL, 'DC x21']]
        self.assertEqual(self.parsed, expected)

    def test_casterLevel(self):
        """
        Quals containing caster level get parsed
        """
        self.parser("caster level 8th").apply("qualInner")
        expected = [[sxp.CL, 8]]
        self.assertEqual(self.parsed, expected)

        self.parsed = []
        self.parser("caster level sux").apply("qualInner")
        expected = [[sxp.QUAL, 'caster level sux']]
        self.assertEqual(self.parsed, expected)

    def test_combo(self):
        """
        Various combinations of vanilla, DC and caster level get parsed
        """
        self.parser("caster level 8th, peanut butter").apply("qualInner")
        expected = [[sxp.CL, 8], [sxp.QUAL, "peanut butter"]]
        self.assertEqual(self.parsed, expected)

        self.parsed = []
        actual = self.parser("DC 8, peanut butter, caster level 8th").apply("qualInner")
        expected = [[sxp.DC, 8], [sxp.QUAL, "peanut butter"], [sxp.CL, 8]]
        self.assertEqual(self.parsed, expected)

    def test_vanilla(self):
        """
        Vanilla non-interesting quals just get a QUAL marker
        """
        t = "whatever 123 aasdf"
        self.parser(t).apply("qualInner")
        expected = [[sxp.QUAL, "whatever 123 aasdf"]]
        self.assertEqual(self.parsed, expected)

        self.parsed = []
        t = "whatever 123, aasdf"
        self.parser(t).apply("qualInner")
        expected = [[sxp.QUAL, "whatever 123"], [sxp.QUAL, "aasdf"]]
        self.assertEqual(self.parsed, expected)


class PreprocTest(unittest.TestCase, DiffTestCaseMixin):
    """
    Test the preprocessor and support functions
    """
    def test_joinRaw(self):
        """
        Consecutive sequences of RAW get joined together; other stuff left
        alone
        """
        t = [(sxp.RAW, "1"), (sxp.QUAL, "2"), (sxp.RAW, "3"),
                (sxp.RAW, "4"), (sxp.RAW, "56"), (sxp.FSTART, "whatever")]
        expected = [(sxp.RAW, "1"), (sxp.QUAL, "2"), (sxp.RAW, "3456"),
                (sxp.FSTART, "whatever")]
        self.assertEqual(sxp.joinRaw(t), expected)

    def test_preprocess(self):
        """
        Convert unprocessed XML nodes into preprocessed SLA nodes
        """
        test = """<div level="8" topic="Spell-Like Abilities">
        <p><b>Spell-Like Abilities:</b> At will-<i>detect evil</i> (as a free action);
        1/day-<i>cure moderate wounds</i> (Caster level 5th),
        <i>neutralize poison</i> (DC 21, caster level 8th) (with a touch of its horn),
        <i>greater teleport</i> (anywhere within its home; it cannot teleport beyond the forest boundaries nor back from outside). The save DC is Charisma-based.</p>
        </div>"""

        n = minidom.parseString(test).documentElement
        try:
            sxp.preprocessSLAXML(n)
        except Exception, e:
            import sys, pdb
            print sys.exc_info()
            pdb.post_mortem(sys.exc_info()[2])
        actual = unicode.splitlines(n.toprettyxml(indent=""))
        expected = unicode.splitlines(inspect.cleandoc(
        u'''<div level="8" topic="Spell-Like Abilities" xmlns:p="http://goonmill.org/2007/property.n3#">
         
        <p>
        <b p:property="powerName">
        Spell-Like Abilities:
        </b>
        <span content="At will" p:property="frequencyStart"/>
        At will-
        <i p:property="spellName">
        detect evil
        </i>
         
        <span p:property="qualifier">
        (as a free action)
        </span>
        <span p:property="sep"/>
        ;
         
        <span content="1/day" p:property="frequencyStart"/>
        1/day-
        <i p:property="spellName">
        cure moderate wounds
        </i>
         
        <span p:property="qualifier">
        (Caster level 5th)
        </span>
        <span p:property="sep"/>
        ,
         
        <i p:property="spellName">
        neutralize poison
        </i>
         
        <span content="21" p:property="dc">
        (DC 21)
        </span>
        <span content="8" p:property="casterLevel">
        (caster level 8)
        </span>
         
        <span p:property="qualifier">
        (with a touch of its horn)
        </span>
        <span p:property="sep"/>
        ,
         
        <i p:property="spellName">
        greater teleport
        </i>
         
        <span p:property="qualifier">
        (anywhere within its home; it cannot teleport beyond the forest boundaries nor back from outside)
        </span>
        <span p:property="sep"/>
        .
         The save DC is Charisma-based
        <span p:property="sep"/>
        .
        </p>
         
        </div>
        '''))
        self.failIfDiff(actual, expected, fromfile="actual", tofile="expected")

    # t2 = '''<div level="8" topic="Spell-Like Abilities">
    #         <p><b>Spell-Like Abilities:</b> At will-<i>greater dispel
    #         magic</i>,  <i>displacement</i> (DC 18),  <i>greater
    #         invisibility</i> (DC 19),  <i>ethereal jaunt</i>. Caster level
    #         22nd. The save DCs are Charisma-based.</p>
    #         </div>'''

