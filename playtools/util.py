import os

def sibpath(path, sibling):
    """Return the path to a sibling of a file in the filesystem.

    This is useful in conjunction with the special __file__ attribute
    that Python provides for modules, so modules can load associated
    resource files.

    COPY/PASTED from twisted.python.util so as not to have a dependency on
    twisted for this little thing.
    """
    return os.path.join(os.path.dirname(os.path.abspath(path)), sibling)

RESOURCE = lambda f: sibpath(__file__, f)
