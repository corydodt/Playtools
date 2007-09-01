from zope.interface import implements

from twisted.plugin import IPlugin

from playtools.convert import IConverter

class SkillConverter(object):
    implements(IConverter, IPlugin)

    def getNextItem(self):
        TODO

    def writePlaytoolsItem(self, playtoolsIO):
        TODO2

    """
    CREATE TABLE skill (
      id INTEGER PRIMARY KEY,
      name varchar(100) NOT NULL default '',
      subtype longtext,
      key_ability varchar(255) default '',
      psionic varchar(255) default '',
      trained varchar(255) default '',
      armor_check varchar(255) default '',
      description longtext,
      skill_check longtext,
      action longtext,
      try_again longtext,
      special longtext,
      restriction longtext,
      synergy longtext,
      epic_use longtext,
      untrained longtext,
      full_text longtext,
      reference varchar(255) default ''
    );
    """

skillConverter = SkillConverter()
