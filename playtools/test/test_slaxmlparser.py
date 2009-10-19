"""
test_slaxmlparser verifies the processes that convert XML nodes containing spell-like abilities
into formed XML structures.
"""
import inspect
from xml.dom import minidom

from twisted.trial import unittest

from playtools.parser import slaxmlparser as sxp
from playtools.test.pttestutil import DiffTestCaseMixin

class PreprocessorTest(unittest.TestCase, DiffTestCaseMixin):
    def setUp(self):
        globs = {'QUAL': sxp.QUAL, 'DC': sxp.DC, 'CL': sxp.CL, 'RAW': sxp.RAW,
                'SEP': sxp.SEP, 'DCBASIS': sxp.DCBASIS, 'DCTOP': sxp.DCTOP,
                'CLTOP': sxp.CLTOP}
        self._parsed = []
        globs['A'] = lambda *x: self._parsed.extend(x)
        self.parser = sxp.OMeta.makeGrammar(sxp.preprocGrammar, globs, "Preprocessor")

    def applyRule(self, test, rule):  
        """
        Apply a testing rule, then return the result which was stored on self
        """
        self.parser(test).apply(rule)
        p = self._parsed
        self._parsed = []
        return p


class RemainderTest(PreprocessorTest):
    """
    Test how the remainder (part after the end of all spell frequency blocks)
    parses - need caster level, dc, dc basis.
    """
    def test_dcBasis(self):
        actual = self.applyRule("The save DCs are Charisma-based", "remainder")
        expected = [[sxp.DCBASIS, u"charisma"]]
        self.assertEqual(actual, expected)

        actual = self.applyRule("The save DC is Strength-based", "remainder")
        expected = [[sxp.DCBASIS, u"strength"]]
        self.assertEqual(actual, expected)

    def test_casterLevel(self):
        actual = self.applyRule(" Caster level 30", "remainder")
        expected = [[sxp.CLTOP, 30]]
        self.assertEqual(actual, expected)

        actual = self.applyRule(" Caster level 30th", "remainder")
        expected = [[sxp.CLTOP, 30]]
        self.assertEqual(actual, expected)

        actual = self.applyRule("Caster level equals the barghest's HD", "remainder")
        expected = [[sxp.CLTOP, "equals the barghest's HD"]]
        self.assertEqual(actual, expected)

    def test_dcTop(self):
        actual = self.applyRule("save DC\n26 + spell level", "remainder")
        expected = [[sxp.DCTOP, u"26 + spell level"]]
        self.assertEqual(actual, expected)

        actual = self.applyRule("save DC 26", "remainder")
        expected = [[sxp.DCTOP, 26]]
        self.assertEqual(actual, expected)

    def test_vanilla(self):
        actual = self.applyRule("Some bullshit", "remainder")
        expected = [[sxp.RAW, u"Some bullshit"]]
        self.assertEqual(actual, expected)

    def test_remainderAll(self):
        t = inspect.cleandoc("""Some bullshit. Caster level 30th; save DC 26 + spell level.
        The save DCs are Charisma-based.""")
        actual = self.applyRule(t, "remainder")
        expected = [[sxp.RAW, "Some bullshit"], [sxp.CL, 30], 
            [sxp.DC, u"26 + spell level"], [sxp.DCBASIS, "charisma"]]


class QualTest(PreprocessorTest):
    """
    Test the parsing of quals
    """
    def test_DC(self):
        """
        Quals containing DC get parsed
        """
        actual = self.applyRule("DC 21", "qualInner")
        expected = [[sxp.DC, 21]]
        self.assertEqual(actual, expected)

        actual = self.applyRule("DC x21", "qualInner")
        expected = [[sxp.QUAL, 'DC x21']]
        self.assertEqual(actual, expected)

    def test_casterLevel(self):
        """
        Quals containing caster level get parsed
        """
        actual = self.applyRule("caster level\n8th", "qualInner")
        expected = [[sxp.CL, 8]]
        self.assertEqual(actual, expected)

        actual = self.applyRule("caster level sux", "qualInner")
        expected = [[sxp.QUAL, 'caster level sux']]
        self.assertEqual(actual, expected)

    def test_combo(self):
        """
        Various combinations of vanilla, DC and caster level get parsed
        """
        actual = self.applyRule("caster level 8th, peanut butter", "qualInner")
        expected = [[sxp.CL, 8], [sxp.QUAL, "peanut butter"]]
        self.assertEqual(actual, expected)

        actual = self.applyRule("DC 8, peanut butter, caster level 8th", "qualInner")
        expected = [[sxp.DC, 8], [sxp.QUAL, "peanut butter"], [sxp.CL, 8]]
        self.assertEqual(actual, expected)

    def test_vanilla(self):
        """
        Vanilla non-interesting quals just get a QUAL marker
        """
        t = "whatever 123 aasdf"
        actual = self.applyRule(t, "qualInner")
        expected = [[sxp.QUAL, "whatever 123 aasdf"]]
        self.assertEqual(actual, expected)

        t = "whatever 123, aasdf"
        actual = self.applyRule(t, "qualInner")
        expected = [[sxp.QUAL, "whatever 123"], [sxp.QUAL, "aasdf"]]
        self.assertEqual(actual, expected)


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
        test = inspect.cleandoc("""<div level="8" topic="Spell-Like Abilities">
        <p><b>Spell-Like Abilities:</b> At will-<i>detect evil</i> (as a free action);
        1/day-<i>cure moderate wounds</i> (Caster level 5th),
        <i>neutralize poison</i> (DC 21, caster level 8th) (with a touch of its horn),
        <i>greater teleport</i> (anywhere within its home; it cannot teleport
        beyond the forest boundaries nor back from outside). Caster level
        30th; save DC 26 + spell level.
        The save DC is Charisma-based.</p>
        </div>""")

        n = minidom.parseString(test).documentElement
        n2 = sxp.preprocessSLAXML(n)
        actual = unicode.splitlines(n2.toprettyxml(indent=""))
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
         
        <span content="5" p:property="casterLevel">
        (caster level 5)
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
        (anywhere within its home; it cannot teleport
        beyond the forest boundaries nor back from outside)
        </span>
        <span p:property="sep"/>
        .
        <span content="30" p:property="casterLevel">
        Caster level 30
        </span>
        <span p:property="sep"/>
        ;
        <span content="26 + spell level" p:property="dc">
        save DC 26 + spell level
        </span>
        <span p:property="sep"/>
        .
        <span content="charisma" p:property="saveDCBasis">
        The save DCs are Charisma-based
        </span>
        <span p:property="sep"/>
        .
        </p>
         
        </div>
        '''))

        self.failIfDiff(actual, expected, fromfile="actual", tofile="expected")

        # test that preprocessing is idempotent
        sxp.preprocessSLAXML(n)
        sxp.preprocessSLAXML(n)
        actual = unicode.splitlines(n.toprettyxml(indent=""))

        self.failIfDiff(actual, expected, fromfile="actual", tofile="expected")


        # t2 = inspect.cleandoc('''<div level="8" topic="Spell-Like Abilities">
        #         <p><b>Spell-Like Abilities:</b> At will-<i>greater dispel
        #         magic</i>,  <i>displacement</i> (DC 18),  <i>greater
        #         invisibility</i> (DC 19),  <i>ethereal jaunt</i>. Caster level
        #         22nd. The save DCs are Charisma-based.</p>
        #         </div>''')


class RDFaProcessTest(unittest.TestCase, DiffTestCaseMixin):
    def setUp(self):
        self._parsed = sxp.NodeTree()
        globs = {'t': self._parsed, 'isProp': sxp.isProp, 'isWS': sxp.isWS, 
                'isSepText': sxp.isSepText,
                 'ww':lambda *x: None ,
                 # 'ww': sxp.debugWrite
                }
        self.parser = sxp.OMeta.makeGrammar(sxp.rdfaGrammar, globs,
                "RDFaParser")

    def applyRule(self, test, rule):  
        """
        Apply a testing rule, then return the result which was stored on self
        """
        self._parsed.useNode(minidom.parseString('''<div xmlns:p=
                "http://goonmill.org/2007/property.n3#">{0}</div>'''.format(test)))
        seq = sxp.flattenSLATree(self._parsed.node.documentElement)
        self.parser(seq).apply(rule)
        return self._parsed.node

    def test_ws(self):
        """
        Whitespace is correctly seen
        """
        test = inspect.cleandoc(u"""  	  
        """)
        ret = self.applyRule(test, 'ws')
        actual = ret.documentElement.childNodes[0]
        self.assertEqual(actual.data.strip(), u'')

    def test_frequency(self):
        """
        Frequency wrappers get replaced correctly
        """
        test = inspect.cleandoc(u"""<span content="At will" p:property="frequencyStart" />
            At will-<i p:property="spellName">detect evil</i> <span
            p:property="qualifier">(as a free\naction)</span> <span
            p:property="casterLevel">(caster level 9th)</span> <span
            p:property="dc">(DC 19)</span> <span p:property="sep"/>""")
        ret = self.applyRule(test, 'fGroup')
        actual = ret.documentElement.childNodes[0].toprettyxml(indent=u"").splitlines()
        expected = inspect.cleandoc(u"""<span content="At will" p:property="frequencyGroup">
             
                         At will-
             
             <span content="detect evil" p:property="spell">
             <i p:property="spellName">
             detect evil
             </i>
              
             <span p:property="qualifier">
             (as a free
             action)
             </span>
              
             <span p:property="casterLevel">
             (caster level 9th)
             </span>
              
             <span p:property="dc">
             (DC 19)
             </span>
             </span>
             </span>""").splitlines()
        self.failIfDiff(actual, expected, 'actual', 'expected')

    def test_spell(self):
        """
        Spells get wrapped correctly, containing all quals
        """
        test = inspect.cleandoc(u"""<i p:property="spellName">neutralize poison</i>
        <span content="21" p:property="dc">(DC 21)</span>
        <span content="8" p:property="casterLevel">(caster level 8)</span>
        <span p:property="qualifier">(with a touch of its horn)</span>
        <span p:property="sep"/>""")
        ret = self.applyRule(test, 'spell')
        actual = ret.documentElement.toprettyxml(indent=u"").splitlines()
        expected = inspect.cleandoc(u"""<div xmlns:p="http://goonmill.org/2007/property.n3#">
        
        
        <span content="neutralize poison" p:property="spell">
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
        </span>
        </div>""").splitlines()
        self.failIfDiff(actual, expected, 'actual', 'expected')

    def test_rdfaProcess(self):
        """
        Original XML gets fixed up correctly with RDFa nodes
        """
        test = inspect.cleandoc(u'''<div level="8" topic=
        "Spell-Like Abilities" xmlns:p=
        "http://goonmill.org/2007/property.n3#"> <p><b p:property=
        "powerName">Spell-Like Abilities:</b><span content="At will" p:property=
        "frequencyStart"/>At will-<i p:property=
        "spellName">detect evil</i> <span p:property=
        "qualifier">(as a free action)</span><span p:property=
        "sep"/>; <span content="1/day" p:property=
        "frequencyStart"/>1/day-<i p:property=
        "spellName">cure moderate wounds</i> <span content="5" p:property=
        "casterLevel">(caster level 5)</span><span p:property=
        "sep"/>, <i p:property=
        "spellName">neutralize poison</i> <span content="21" p:property=
        "dc">(DC 21)</span><span content="8" p:property=
        "casterLevel">(caster level 8)</span> <span p:property=
        "qualifier">(with a touch of its horn)</span><span p:property=
        "sep"/>, <i p:property=
        "spellName">greater teleport</i> <span p:property=
        "qualifier">(anywhere within its home; it cannot teleport
        beyond the forest boundaries nor back from outside)</span><span p:property=
        "sep"/>.<span content="30" p:property=
        "casterLevel">Caster level 30</span><span p:property=
        "sep"/>;<span content="26 + spell level" p:property=
        "dc">save DC 26 + spell level</span><span p:property=
        "sep"/>.<span content="charisma" p:property=
        "saveDCBasis">The save DCs are Charisma-based</span><span p:property=
        "sep"/>.</p> </div>''')
        preproc = minidom.parseString(test)
        
        n2 = sxp.rdfaProcessSLAXML(preproc)
        actual = unicode.splitlines(n2.documentElement.toprettyxml(indent=""))
        expected = unicode.splitlines(inspect.cleandoc(
        u'''<div level="8" topic="Spell-Like Abilities" xmlns:p="http://goonmill.org/2007/property.n3#">
         
        <p>
        <b p:property="powerName">
        Spell-Like Abilities:
        </b>
        <span content="At will" p:property="frequencyGroup">
        At will-
        
        <span content="detect evil" p:property="spell">
        <i p:property="spellName">
        detect evil
        </i>
         
        <span p:property="qualifier">
        (as a free action)
        </span>
        </span>
        </span>
        ; 
        <span content="1/day" p:property="frequencyGroup">
        1/day-
        
        <span content="cure moderate wounds" p:property="spell">
        <i p:property="spellName">
        cure moderate wounds
        </i>
         
        <span content="5" p:property="casterLevel">
        (caster level 5)
        </span>
        </span>
        , 
        <span content="neutralize poison" p:property="spell">
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
        </span>
        , 
        <span content="greater teleport" p:property="spell">
        <i p:property="spellName">
        greater teleport
        </i>
         
        <span p:property="qualifier">
        (anywhere within its home; it cannot teleport
        beyond the forest boundaries nor back from outside)
        </span>
        </span>
        </span>
        .
        <span content="30" p:property="casterLevel">
        Caster level 30
        </span>
        ;
        <span content="26 + spell level" p:property="dc">
        save DC 26 + spell level
        </span>
        .
        <span content="charisma" p:property="saveDCBasis">
        The save DCs are Charisma-based
        </span>
        .
        </p>
         
        </div>
        '''))

        self.failIfDiff(actual, expected, fromfile="actual", tofile="expected")

        # verify you can't process it twice
        self.assertRaises(sxp.AlreadyParsed, sxp.rdfaProcessSLAXML, n2)


class DocumentTest(unittest.TestCase, DiffTestCaseMixin):
    """
    Test that the tested operations work when applied in sequence to an entire
    document
    """
    def test_findEligibleSLAs(self):
        """
        The correct list of SLAs is returned
        """
        t1 = inspect.cleandoc(u"""<html xmlns:p="http://goonmill.org/2007/property.n3">
            <div level="8" id="a" topic="Stuff"></div>
            <div level="8" id="b" topic="Spell-Like Abilities">At will-<i>charm monster</i></div>
            <div level="8" id="c" topic="Other Spell-Like Abilities">At will-<i>charm monster</i></div>
            <div level="8" id="d" topic="Other Spell-Like Abilities"><span p:property="frequencyGroup">At will-<i>charm monster</i></span></div>
            </html>""")
        doc = minidom.parseString(t1)
        act = []
        for n in sxp.findEligibleSLAs(doc):
            act.append(n.toxml())
        ex = [u'<div id="b" level="8" topic="Spell-Like Abilities">At will-<i>charm monster</i></div>',
              u'<div id="c" level="8" topic="Other Spell-Like Abilities">At will-<i>charm monster</i></div>',
              ]
        self.assertNoDiff(act, ex, 'actual', 'expected')

        t2 = inspect.cleandoc("""<div level="8" id="d" topic="Spell-Like Abilities">this one doesn't count</div>""")
        doc = minidom.parseString(t2)
        finder = sxp.findEligibleSLAs(doc)
        self.assertRaises(AssertionError, finder.next)

    def test_processDocument(self):
        """
        A document can be parsed to produce an rdfa-enhanced document.
        """
        test = inspect.cleandoc("""<html xmlns:p=
        "http://goonmill.org/2007/property.n3#"><div level="8" topic="Spell-Like Abilities">
        <p><b>Spell-Like Abilities:</b> At will-<i>detect evil</i> (as a free action);
        1/day-<i>cure moderate wounds</i> (Caster level 5th),
        <i>neutralize poison</i> (DC 21, caster level 8th) (with a touch of its horn),
        <i>greater teleport</i> (anywhere within its home; it cannot teleport
        beyond the forest boundaries nor back from outside).  Caster level 30;
        save DC 26 + spell level.  The save DCs are Charisma-based.</p>
        </div></html>""")
        doc = minidom.parseString(test)
        doc = sxp.processDocument(doc)

        actual = unicode.splitlines(doc.toprettyxml(indent=""))
        expected = unicode.splitlines(inspect.cleandoc(
        u'''<?xml version="1.0" ?>
        <html xmlns:p="http://goonmill.org/2007/property.n3#">
        <div level="8" topic="Spell-Like Abilities">
         
        <p>
        <b p:property="powerName">
        Spell-Like Abilities:
        </b>
        <span content="At will" p:property="frequencyGroup">
        At will-
        
        <span content="detect evil" p:property="spell">
        <i p:property="spellName">
        detect evil
        </i>
         
        <span p:property="qualifier">
        (as a free action)
        </span>
        </span>
        </span>
        ;
         
        <span content="1/day" p:property="frequencyGroup">
        1/day-
        
        <span content="cure moderate wounds" p:property="spell">
        <i p:property="spellName">
        cure moderate wounds
        </i>
         
        <span content="5" p:property="casterLevel">
        (caster level 5)
        </span>
        </span>
        , 
        <span content="neutralize poison" p:property="spell">
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
        </span>
        , 
        <span content="greater teleport" p:property="spell">
        <i p:property="spellName">
        greater teleport
        </i>
         
        <span p:property="qualifier">
        (anywhere within its home; it cannot teleport
        beyond the forest boundaries nor back from outside)
        </span>
        </span>
        </span>
        .
        <span content="30" p:property="casterLevel">
        Caster level 30
        </span>
        ;
        <span content="26 + spell level" p:property="dc">
        save DC 26 + spell level
        </span>
        .
        <span content="charisma" p:property="saveDCBasis">
        The save DCs are Charisma-based
        </span>
        .
        </p>
         
        </div>
        </html>
        '''))
        self.failIfDiff(actual, expected, 'actual', 'expected')
