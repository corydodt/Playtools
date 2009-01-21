try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages
setup(name='Playtools',
      version='0.1.1',
      author='Cory Dodt',
      description='Playtools for RPG Software',
      url='http://goonmill.org/playtools/',
      download_url='http://playtools-source.goonmill.org/archive/tip.tar.gz',

      packages=find_packages(),

      scripts=['bin/ptconvert', 'bin/ptstore'],

      install_requires=[
          'pysqlite>=2',
          'storm>=0.13',
          'rdflib<3a',
          ],

      package_data={
          'playtools': ['data/*.n3',
              'static/*.png',
              '*.n3',
              'plugins/*.n3',
              'test/*.n3',
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
