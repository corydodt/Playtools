#!/bin/bash
## Bootstrap setup for goonmill

umask 002

if [ "$1" == "force" ]; then
    force="force"
else
    force=""
fi

cat <<EOF
:: This script will check your environment to make sure Goonmill is
:: ready to run, and do any one-time setup steps necessary.
::
:: Please check for any errors below, and fix them.
EOF

export errorStatus=""

function testPython()
# Use: testPython "Software name" "python code"
#  If "python code" has no output, we pass.
# 
#  If there is any output, the last line is considered an error message, and
#  we print it.  Then we set the global errorStatus.
# 
#  "python code" should not write to stderr if possible, so use 2>&1 to
#  redirect to stdout.
{
    software="$1"
    line=$(python -c "$2" 2>&1 | tail -1)

    if [ -n "$line" ]; then
        echo "** Install $software ($line)"
        errorStatus="error"
    else
        echo "OK $software"
    fi
}

testPython "RDFlib == 2.4.1" 'from rdflib import __version__ as v; assert v>="2.4.1"'
testPython "RDFalchemy > 0.2b2" 'from rdfalchemy import rdfsSubject'
testPython "Storm" 'import storm.locals'
testPython "pysqlite2" 'import pysqlite2'
testPython "simpleparse" 'import simpleparse'
testPython "Hypy" 'from hypy import *'
testPython "Python 2.5" 'import xml.etree'

if [ "$errorStatus" == "error" ]; then
    echo "** Errors occurred.  Please fix the above errors, then re-run this script."
    exit 1
fi

if [ -n "$force" ]; then
    echo ::
    echo ':: force is in effect: removing database files!'
    set -x
    rm -f playtools/rdflib.db*
    rm -rf playtools/plugins/srd35-index/
    set +x
fi

tripledb=playtools/rdflib.db
if [ ! -r "$tripledb" ]; then
    echo ::
    echo :: $tripledb
    ptstore create $tripledb
    ns=("--n3 http://www.w3.org/2000/01/rdf-schema#"
        "--n3 http://goonmill.org/2007/family.n3#"
        "--n3 http://goonmill.org/2007/characteristic.n3#"
        "--n3 http://goonmill.org/2007/property.n3#"
        "--n3 http://goonmill.org/2007/skill.n3#"
        "--n3 http://goonmill.org/2007/feat.n3#"
        "--n3 http://goonmill.org/2009/statblock.n3#"
        )
    ptstore pull --verbose ${ns[@]} $tripledb || exit 1
else
    echo "** ${tripledb} already exists, not willing to overwrite it!"
    echo ::
    echo :: If you have already run bootstrap.sh once, this is not an error.
    echo ::
fi

estraierindex=playtools/search-index/_idx
if [ ! -d "$estraierindex" ]; then
    echo ::
    echo :: $estraierindex
    python playtools/search.py --build-index
    echo
else
    echo "** ${estraierindex} already exists, not willing to overwrite it!"
    echo ::
    echo :: If you have already run bootstrap.sh once, this is not an error.
    echo ::
fi

echo "Done."
