"""
Some config settings for launching srd35 database.

This is a separate module so I can import it without importing the plugin
itself first.
"""
from playtools.util import RESOURCE
SQLPATH = RESOURCE('plugins/srd35.db')
RDFPATH = RESOURCE('plugins/srd35rdf.db')
