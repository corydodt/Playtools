"""
Mercurial hooks for this repo
See help("goonmill.hg") package for use
"""
import os


class HookDRunner(object):
    """Run everything in hook.d"""
    extension = None

    def __call__(self, ui, repo, **kw):
        ## node = bin(kw['node'])
        os.chdir(repo.path + '/..')
        s = "for f in hook.d/*.%s; do bash $f %s; done" % (
                self.__class__.extension, kw['node'],)
        os.system(s)

class ChangegroupRunner(HookDRunner):
    extension = 'changegroup'

class CommitRunner(HookDRunner):
    extension = 'commit'

changegroupRunner = ChangegroupRunner()
commitRunner = CommitRunner()
