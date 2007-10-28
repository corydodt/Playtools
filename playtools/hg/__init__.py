"""Mercurial stuff

To use, add

[extensions]
goonmillext = /usr/local/Goonmill/goonmill/hg/hooks.py

[hooks]
changegroup.hookd = goonmillext.changegroupRunner
commit.hookd = goonmillext.commitRunner

And create a hook.d directory in `hg root`

"""
