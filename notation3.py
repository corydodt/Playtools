import sys

from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers

grammar = r'''# The N3 Full Grammar
# in XML formal grammar notation
# which see  http://www.w3.org/TR/2004/REC-xml11-20040204/#sec-notation
# and see http://en.wikipedia.org/wiki/Extended_Backus-Naur_form
#
# $Id: notation3.bnf,v 1.14 2006/06/22 22:03:21 connolly Exp $
# transcribe from n3.n3 revision 1.28 date: 2006/02/15 15:49:00

# Edited by CDD to make parseable by simpleparse

# yeah, we need whitespace - CDD
<wsc> := [ \t\n\r]
<ws> := wsc+

# label these things so the parser can emit syntax highlights for them
comma := ","
period := "."
semi := ";"

>document< := (ws / comment / closedStatement)*
>closedStatement< := statement, ws?, !, statementTerminator
>statementTerminator< := (semi, ws?)?, period

comment := "#", ( '"' / NameChar3x / [ \t] / ECHAR / UCHAR)*

>statement< := !, declaration/universal/existential/simpleStatement/formula

# formulas don't need a closing . on a statement
>formulacontent< := statement, ws?, (statementTerminator, ws?, statement)*
>formula< := formulaStart, ws?, formulacontent?, statementTerminator?, ws?, !, formulaEnd

>universal< := forAllKeyword, ws, !, varlist
>forAllKeyword< := "@forAll"

>existential< := forSomeKeyword, ws, !, varlist
>forSomeKeyword< := "@forSome"

>varlist< := (symbol, (ws?, comma, ws?, symbol)*)?

>declaration< := prefixKeyword, ws, !, prefix, ws, !, uriref/keywordsKeyword,
               (ws, barename, ws?, (comma, ws?, barename)*)?
keywordsKeyword := "@keywords"
prefixKeyword := "@prefix"

>barename< := qname
# barename constraint: no colon

>simpleStatement< := term, ws, !, propertylist

>propertylist< := (property, (ws?, semi, ws?, property)*)?
>property< := ?-(period), !, (verb / inverb), ws, !, term, (ws?, comma, ws?, !, term)*


>verb< := (hasKeyword, ws)?, !, term/verbOperator
hasKeyword := "@has"
verbOperator := "a"/"=>"/"<="/"="


>inverb< := isKeyword, !, ws, !, term, !, ws, !, ofKeyword
isKeyword := "@is"
ofKeyword := "@of"

>term< := pathitem, (ws?, pathtail)?

>pathtail< := (pathtailBang, !, term)/(pathtailCaret, !, term)
pathtailBang := "!"
pathtailCaret := "^"

>pathitem< := symbol / evar / uvar / numeral / literal / formula /
        (propertylistStart, ws?, !, propertylist, ws?, propertylistEnd) / 
        (listStart, ws?, !, term*, ws?, listEnd) / boolean
formulaStart := "{"
formulaEnd := "}"
propertylistStart := "["
propertylistEnd := "]"
listStart := "("
listEnd := ")"

literal := STRING_LITERAL_LONG2 / STRING_LITERAL2 / (literalDoubleCaret, !, symbol) / langstring
literalDoubleCaret := "^^"

boolean := "@true" / "@false"

>symbol< := uriref / qname

>numeral< := integer / double / decimal

# @terminals  -- is this a comment in BNF?  made it a comment.  - CDD

>integer< := [+-]?, [0-9]+
>double<    := [+-]?, [0-9]+, (period, [0-9]+)?, ( [eE], [+-]?, [0-9]+)
>decimal<    := [+-]?, [0-9]+, (period, [0-9]+)?

# modified to match more closely n3.n3, and because it wasn't parseable by
# simpleparse - CDD
uriref :=    '<', !, [-.a-zA-Z:/%+&?#0-9]*, '>'

>qname< := prefix?, localname
>localname< := (NameStartChar3/"_"), NameChar3*
prefix := (("_", NameChar3+) / (NameStartChar3, NameChar3*))?, ":"

# @@ no \u stuff, for now
>NameStartChar3< :=   [A-Z] / [a-z]

# @@ no \u stuff
>NameChar3< :=   NameStartChar3 / "-" / "_" / [0-9]

# NameStartChar    from xml11, less ":", "_"
>NameStartChar3x< :=   [A-Z] / [a-z] / [#xC0-#xD6]
      / [#xD8-#xF6] / [#xF8-#x2FF] / [#x370-#x37D] / [#x37F-#x1FFF]
      / [#x200C-#x200D] / [#x2070-#x218F] / [#x2C00-#x2FEF]
      / [#x3001-#xD7FF] / [#xF900-#xFDCF] / [#xFDF0-#xFFFD]
      / [#x10000-#xEFFFF]

# NameChar from xml11 less ":" and period, plus "_"
# added [] around #xB7 so simpleparse could parse - CDD
>NameChar3x< :=   NameStartChar3 / "-" / "_"
    / [0-9] / [#xB7] / [#x0300-#x036F] / [#x203F-#x2040]


>evar< := "_:", localname
>uvar< := "?", localname

>langstring< := (STRING_LITERAL_LONG2 / STRING_LITERAL2), "@", [a-z]+, ("-", [a-z0-9]+)*

trips := '"""'
>STRING_LITERAL_LONG2< := trips, (?-trips, ('\\"' / ANY_CHAR) )*, !, trips
>STRING_LITERAL2< := '"', ('\\"' / -["\n\r])*, !, '"'
>ANY_CHAR< := -[]]

# added [] around #x5C - CDD
>ECHAR< := [#x5C], [tbnrf#x5C#x22']

>UCHAR<    :=   "\\", ( ("u", HEX, HEX, HEX, HEX) / ("U", HEX, HEX, HEX, HEX, HEX, HEX, HEX, HEX) )
>HEX<      :=   [0-9] / [A-F] / [a-f]
'''

n3Parser = parser.Parser(grammar, root='document')

class Processor(disp.DispatchProcessor):
    def operator(self, (t,s1,s2,sub), buffer):
        print 'operator', disp.getString((t,s1,s2,sub), buffer)

    semi = pathtailBang = pathtailCaret = hasKeyword = verbKeyword = isKeyword = prefixKeyword = ofKeyword = period = comma = boolean = literalDoubleCaret = operator

    def literal(self, (t,s1,s2,sub), buffer):
        print 'literal', repr(disp.getString((t,s1,s2,sub), buffer))

    def comment(self, (t,s1,s2,sub), buffer):
        print 'comment', disp.getString((t,s1,s2,sub), buffer)

    def uriref(self, (t,s1,s2,sub), buffer):
        print 'uriref', disp.getString((t,s1,s2,sub), buffer)

    def prefix(self, (t,s1,s2,sub), buffer):
        print 'prefix', disp.getString((t,s1,s2,sub), buffer)

if __name__ == '__main__':
    s = open(sys.argv[1])
    p = n3Parser.parse(s.read(), processor=Processor())
    import pdb; pdb.set_trace()
