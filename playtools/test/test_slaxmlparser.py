"""
test_slaxmlparser verifies the processes that convert XML nodes containing spell-like abilities
into formed XML structures.
"""
from xml.dom import minidom
from twisted.trial import unittest

from playtools.parser import slaxmlparser as sxp
from playtools.test.pttestutil import DiffTestCaseMixin

class QualizerTest(unittest.TestCase, DiffTestCaseMixin):
    """
    Test the Qualizer and support functions
    """
    def setUp(self):
        globs = {'QUAL': sxp.QUAL, 'DC': sxp.DC, 'CL': sxp.CL}
        Preprocessor = sxp.OMeta.makeGrammar(sxp.preprocGrammar, globs, "Preprocessor")
        self.qualizer = Preprocessor.makeGrammar(sxp.qualGrammar, globs, "Qualizer")

    def test_DC(self):
        """
        Quals containing DC get parsed
        """
        actual = self.qualizer("DC 21").apply("qual")
        expected = [(sxp.DC, 21)]
        self.assertEqual(actual, expected)

        q = self.qualizer("DC x21")
        self.assertRaises(SyntaxError, q.apply, "qual")

    def test_casterLevel(self):
        """
        Quals containing caster level get parsed
        """
        actual = self.qualizer("caster level 8th").apply("qual")
        expected = [(sxp.CL, 8)]
        self.assertEqual(actual, expected)

        q = self.qualizer("caster level sux")
        self.assertRaises(SyntaxError, q.apply, "qual")

    def test_combo(self):
        """
        Various combinations of vanilla, DC and caster level get parsed
        """
        actual = self.qualizer("caster level 8th, peanut butter").apply("qual")
        expected = [(sxp.CL, 8), (sxp.QUAL, "peanut butter")]
        self.assertEqual(actual, expected)

        actual = self.qualizer("DC 8, peanut butter, caster level 8th").apply("qual")
        expected = [(sxp.DC, 8), (sxp.QUAL, "peanut butter"), (sxp.CL, 8)]
        self.assertEqual(actual, expected)

    def test_vanilla(self):
        """
        Vanilla non-interesting quals just get a QUAL marker
        """
        t = "whatever 123 aasdf"
        actual = self.qualizer(t).apply("qual")
        expected = "whatever 123 aasdf"
        self.assertEqual(actual, expected)

        t = "whatever 123, aasdf"
        actual = self.qualizer(t).apply("qual")
        expected = "whatever 123, aasdf"
        self.assertEqual(actual, expected)


class PreprocTest(unittest.TestCase, DiffTestCaseMixin):
    """
    Test the preprocessor and support functions
    """
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
        self.failIfDiff(*map(unicode.splitlines, [n.toprettyxml(),
            u'''<div level="8" topic="Spell-Like Abilities" xmlns:p="http://goonmill.org/2007/property.n3#">
	 
	<p>
		<b p:property="powerName">
			Spell-Like Abilities:
		</b>
		<div content="At will" p:property="frequencyStart"/>
		At will-
		<i p:property="spellName">
			detect evil
		</i>
		 
		<div p:property="qualifier">
			(as a free action)
		</div>
		<div p:property="sep"/>
		;
		 
		<div content="1/day" p:property="frequencyStart"/>
		1/day-
		<i p:property="spellName">
			cure moderate wounds
		</i>
		 
		<div p:property="qualifier">
			(Caster level 5th)
		</div>
		<div p:property="sep"/>
		,
		 
		<i p:property="spellName">
			neutralize poison
		</i>
		 
		<div p:property="qualifier">
			(
            <div p:property="dc">DC 21</div>
            , caster level 8th)
		</div>
		 
		<div p:property="qualifier">
			(with a touch of its horn)
		</div>
		<div p:property="sep"/>
		,
		 
		<i p:property="spellName">
			greater teleport
		</i>
		 
		<div p:property="qualifier">
			(anywhere within its home; it cannot teleport beyond the forest boundaries nor back from outside)
		</div>
		<div p:property="sep"/>
		.
		 The save DC is Charisma-based
		<div p:property="sep"/>
		.
	</p>
	 
</div>
''']))
    t2 = '''<div level="8" topic="Spell-Like Abilities">
            <p><b>Spell-Like Abilities:</b> At will-<i>greater dispel
            magic</i>,  <i>displacement</i> (DC 18),  <i>greater
            invisibility</i> (DC 19),  <i>ethereal jaunt</i>. Caster level
            22nd. The save DCs are Charisma-based.</p>
            </div>'''

