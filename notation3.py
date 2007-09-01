from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import numbers

grammar = r'''# The N3 Full Grammar
# in XML formal grammar notation
# which see  http://www.w3.org/TR/2004/REC-xml11-20040204/#sec-notation
# and see http://en.wikipedia.org/wiki/Extended_Backus-Naur_form
#
# $Id: notation3.bnf,v 1.14 2006/06/22 22:03:21 connolly Exp $
# transcribe from n3.n3 revision 1.28 date: 2006/02/15 15:49:00

# Edited by CDD to make parseable by simpleparse, as follows:
#  1. Replaced all ::= with :=
#  2. Replaced all "x" "y"  with "x", "y"
#  3. Replaced all "x" | "y" with "x" / "y"
#  4. Rewrote all comments using # instead of /**/
#  5. A handful of specific edits, labeled with "CDD" below
#  6. Addition of ws token as needed
#  7. Addition of ! syntax error token as needed

# yeah, we need whitespace - CDD
<wsc> := [ \t\n\r]
<ws> := wsc+

# label these things so the parser can emit syntax highlights for them
comma := ","
period := "."
semi := ";"

>document< := (ws?, statement, ws?, !, ".", ws?)*

# Formula does NOT need period on last statement

>formulacontent< := (statement, (".", statement)*)?

>statement< := !, declaration/universal/existential/simpleStatement

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

>simpleStatement< := term, !, propertylist

>propertylist< := (ws?, property, (ws?, semi, ws?, property)*)?
>property< := !, (verb / inverb), ws, !, term, (ws?, comma, ws?, !, term)*

>verb< := (hasKeyword, ws)?, !, term/verbOperator
hasKeyword := "@has"
verbOperator := "a"/"="/"=>"/"<="


>inverb< := isKeyword, !, ws, !, term, !, ws, !, ofKeyword
isKeyword := "@is"
ofKeyword := "@of"

>term< := pathitem, (ws?, pathtail)?

>pathtail< := pathtailBang, !, term/pathtailCaret, !, term
pathtailBang := "!"
pathtailCaret := "^"

>pathitem< := symbol / evar / uvar / numeral / literal / 
        (formulaStart, formulacontent, formulaEnd) / 
        (propertylistStart, !, propertylist, propertylistEnd) / 
        (listStart, !, term*, listEnd) / boolean
formulaStart := "{"
formulaEnd := "}"
propertylistStart := "["
propertylistEnd := "]"
listStart := "("
listEnd := ")"

#        / "@this"  #  Deprecated.  Was allowed for this log:forAll x

literal := (STRING_LITERAL2 / STRING_LITERAL_LONG2), (literalDoubleCaret, !, symbol) / langstring
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

>langstring< := (STRING_LITERAL2 / STRING_LITERAL_LONG2), "@", [a-z]+, ("-", [a-z0-9]+)*

# http://www.w3.org/TR/rdf-testcases/#language


# borrow from SPARQL... and double some \\ for yacker (or not?)

>STRING_LITERAL2< := '"', ( NameChar3x / [ \t] / ECHAR / UCHAR)*, '"'

>STRING_LITERAL_LONG2< := '"""', ( ( '"' / '""' )?,
                                 ( NameChar3x / wsc / ECHAR / UCHAR ) )*, '"""'

# added [] around #x5C - CDD
>ECHAR< := [#x5C], [tbnrf#x5C#x22']

# UCHAR from Andy's turtle.html
>UCHAR<    :=   "\\", ( ("u", HEX, HEX, HEX, HEX) / ("U", HEX, HEX, HEX, HEX, HEX, HEX, HEX, HEX) )
>HEX<      :=   [0-9] / [A-F] / [a-f]
'''

n3Parser = parser.Parser(grammar, root='document')

class Processor(disp.DispatchProcessor):
    def operator(self, (t,s1,s2,sub), buffer):
        print 'operator', disp.getString((t,s1,s2,sub), buffer)
    pathtailBang = pathtailCaret = hasKeyword = verbKeyword = isKeyword = prefixKeyword = ofKeyword = uriref = period = comma = boolean = literalDoubleCaret = operator


if __name__ == '__main__':
    s = open('Playtools/playtools/data/family.n3')
    p = n3Parser.parse(s.read(), processor=Processor())
    import pdb; pdb.set_trace()
