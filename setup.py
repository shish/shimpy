import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = ""  # open(os.path.join(here, 'README.md')).read()
CHANGES = ""  # open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'SQLAlchemy',
    'webhelpers',

    #'psycopg2',
    'bbcode',
    'dogpile.cache',
    'flexihash',

    # testing
    'nose',
    'coverage',
    'unittest2',
    'mock',
    'werkzeug',
    ]

setup(name='Shimpy',
      version='0.0',
      description='Shimpy',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Shish',
      author_email='webmaster+shimpy@shishnet.org',
      url='http://github.com/shish/shimpy',
      keywords='web',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='shimpy',
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      start-shimpy = shimpy:main
      """,
      )
