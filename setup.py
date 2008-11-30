from setuptools import setup, find_packages
setup(name='Playtools',
      version='0.1',

      packages=find_packages(),

      scripts=['bin/ptconvert', 'bin/ptstore'],

      install_requires=[
          'pysqlite>=2',
          'storm>=0.13',
          'rdflib>=2.4',
          ],

      package_data={
          'playtools': ['data/*.n3',
              'static/*.png',
              '*.n3',
              'plugins/*.n3',
              'test/*.n3',
              ],
        }
      )
