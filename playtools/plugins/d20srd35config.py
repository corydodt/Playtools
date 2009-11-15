"""
Some config settings for launching srd35 database.

This is a separate module so I can import it without importing the plugin
itself first.
"""
from playtools.util import RESOURCE
from playtools.test.pttestutil import TODO

SQLPATH = RESOURCE('plugins/srd35.db')
RDFPATH = RESOURCE('plugins/srd35rdf.db')

RDFURIS = ['http://www.w3.org/2000/01/rdf-schema#', 
           'http://goonmill.org/2007/family.n3#', 
           'http://goonmill.org/2007/characteristic.n3#', 
           'http://goonmill.org/2007/property.n3#', 
           'http://goonmill.org/2007/skill.n3#', 
           'http://goonmill.org/2007/feat.n3#', 
           'http://goonmill.org/2009/perk.n3#', 
           'http://goonmill.org/2007/monster.n3#'
           ]

SQLS =    ['d20srd35-sql/class.sql', 
           'd20srd35-sql/class_table.sql', 
           'd20srd35-sql/domain.sql', 
           'd20srd35-sql/equipment.sql', 
           'd20srd35-sql/item.sql', 
           'd20srd35-sql/monster.sql', 
           'd20srd35-sql/power.sql', 
           'd20srd35-sql/spell.sql', 
           'd20srd35-sql/__indexes__.sql', 
           ]
