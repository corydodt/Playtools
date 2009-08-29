This is an experiment with using Allen Short's PyMeta to do the dice parsing.
The parser is successfully implemented but I didn't keep going because it
would have required rewriting all of the parsers in here and in Vellumbot.

Some things were not fully implemented:

- I didn't bother to produce an equivalent for "exporting expressions", e.g.
  the dice grammar should be exported to other parsers that use it.  This
  should be a simple matter of making a grammar class for that part of the
  parser.  Clients would call out to it or subclass it.

  (playtools.test.test_diceparser.DiceParserTestCase.test_exportProductions)

- p.t.test_diceparser.DiceParserTestCase.test_parse fails because it's written
  in an odd way.. checks that the length of the successfully parsed expression
  is equal to the length of the original expression which is information that
  is not returned by PyMeta.


.. vim:set ft=rst:
