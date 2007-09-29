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


