"""Playtools for RPG Software"""

from twisted.python.components import globalRegistry
globalRegistry

import playtools.plugins
PLUGINMODULE = playtools.plugins  # making it possible to monkey-patch this in test code

