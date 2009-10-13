try:
    import setuptools
    setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages
setup(name='Playtools',
      version='0.3.0',
      author='Cory Dodt',
      description='Playtools for RPG Software',
      url='http://goonmill.org/playtools/',
      download_url='http://playtools-source.goonmill.org/archive/tip.tar.gz',

      packages=find_packages(),

      scripts=['bin/ptconvert', 'bin/ptstore', 'bin/pt-system-install'],

      install_requires=[
          'Distribute>=0.6.3',
          'pysqlite>=2',
          'storm>=0.13',
          'rdflib==2.4.2_cdd1',
          'SimpleParse>=2.1.0a1,<2.2',
          'twisted>=2.5.0',
          'hypy',
          'fudge',
          'rdfalchemy==0.2b2.svn2',
          ],

      dependency_links=[
          'http://goonmill.org/static/RDFAlchemy-0.2b2.svn2.tar.gz',  # FIXME - svn post 0.2b2 added rdfsSubject which is needed
          'http://goonmill.org/static/rdflib-2.4.2_cdd1.tar.gz',      # FIXME - I patched this to write integers as digits, not typed strings
          'http://softlayer.dl.sourceforge.net/sourceforge/simpleparse/SimpleParse-2.1.0a1.tar.gz', # simpleparse easy_install stopped working, dunno why
          ],

      package_data={
          'playtools': ['data/*.n3',
              '*.n3',
              'plugins/*.n3',
              'test/*.n3',
              'plugins/d20srd35-sql/*.sql',
              'plugins/monster/*.txt',
              'plugins/monster/monstertext/*.htm',
              'parser/specialparser.txt',
              'buildout.cfg',
              'static/*.png',
              ],
        },
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Games/Entertainment :: Role-Playing',
          'Topic :: Software Development :: Libraries',
          ],

      )
