import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = ""  # open(os.path.join(here, 'README.md')).read()
CHANGES = ""  # open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'SQLAlchemy',
    'webhelpers',
    'mako',
    'lesscpy',
    'structlog',
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

    # ext.handle_pixel
    'pillow',
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
      start-shimpy = shimpy.core.server:main

      [shimpy.extensions]
      cmdline = shimpy.ext.cmdline:CmdLine
      alias_editor = shimpy.ext.alias_editor:AliasEditor
      ban_words = shimpy.ext.ban_words:BanWords
      bbcode = shimpy.ext.bbcode:BBCode
      blocks = shimpy.ext.blocks:Blocks
      handle_404 = shimpy.ext.handle_404:Handle404
      hello = shimpy.ext.hello:Hello
      index = shimpy.ext.index:Index
      view = shimpy.ext.view:ViewImage
      statsd = shimpy.ext.statsd:StatsD
      statsd_primer = shimpy.ext.statsd:StatsDPrimer
      rss_images = shimpy.ext.rss_images:RSSImages
      handle_pixel = shimpy.ext.handle_pixel:PixelFileHandler
      custom_html_headers = shimpy.ext.custom_html_headers:CustomHTMLHeaders
      word_filter = shimpy.ext.word_filter:WordFilter
      user_manager = shimpy.ext.user:UserManager
      """,
      )
