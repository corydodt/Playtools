from __future__ import with_statement

import os
import glob

import zc.buildout

import fudge.patcher

class RunTrial(object):
    """
    Use trial to run tests
    """
    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout

    def install(self):
        from twisted.scripts import trial
        argv = ['trial', self.options['what']]
        with fudge.patcher.patched_context('sys', 'argv', argv):
               trial.run()

        return []

    def update(self):
        pass
