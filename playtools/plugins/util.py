"""
Utilities specific to converter plugins, particular anything dealing with
sqlite
"""
from storm.locals import create_database, Store


def srdBoolean(col):
    """
    True if the column is "yes"
    Otherwise False
    """
    if col is None:
        return False
    return col.lower().strip() == "yes"


def initDatabase(dbPath):
    db = create_database('sqlite:%s' % (dbPath,))
    return Store(db)


def cleanSrdXml(s):
    """XML retrieved from the Sqlite SRD databases is
    - encoded in utf8, and
    - escaped on " and \
    this function decodes to unicode and un-escapes
    """
    u = s.decode('utf8')
    u = u.replace(r'\"', '"')
    u = u.replace(r'\n', '\n')
    u = u.replace(r'\\', '\\')
    return u


