.. image:: https://badge.fury.io/py/scrapy-beautifulsoup.svg
     :target: http://badge.fury.io/py/scrapy-beautifulsoup
     :alt: PyPI version

.. image:: https://requires.io/github/alecxe/scrapy-beautifulsoup/requirements.svg?branch=master
     :target: https://requires.io/github/alecxe/scrapy-beautifulsoup/requirements/?branch=master
     :alt: Requirements Status

scrapy-beautifulsoup
====================

Simple Scrapy middleware to process non-well-formed HTML with BeautifulSoup

Installation
============

The package is on PyPI and can be installed with ``pip``:

::

     pip install scrapy-beautifulsoup

Configuration
-------------

Add the middleware to ``DOWNLOADER_MIDDLEWARES`` dictionary setting:

::

    DOWNLOADER_MIDDLEWARES = {
        'scrapy_beautifulsoup.middleware.BeautifulSoupMiddleware': 400
    }


By default, ``BeautifulSoup`` would use the built-in ``html.parser`` parser. To change it, set the ``BEAUTIFULSOUP_PARSER`` setting:

::

    BEAUTIFULSOUP_PARSER = "html5lib"  # or BEAUTIFULSOUP_PARSER = "lxml"

``html5lib`` is an *extremely lenient* parser and, if the target HTML is seriously broken, you might consider being it your first choice. 
Note: `html5lib <https://pypi.python.org/pypi/html5lib>`_ has to be installed in this case:

::

    pip install html5lib

Motivation
==========

`BeautifulSoup <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_ itself with the help of an `underlying parser of choice <https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser>`_ does a pretty good job of handling non-well-formed or broken HTML.
In some cases, it makes sense to pipe the HTML through ``BeautifulSoup`` to "fix" it.

.. |GitHub version| image:: https://badge.fury.io/gh/alecxe%2Fscrapy-beautifulsoup.svg
   :target: http://badge.fury.io/gh/alecxe%2Fscrapy-beautifulsoup
.. |Requirements Status| image:: https://requires.io/github/alecxe/scrapy-beautifulsoup/requirements.svg?branch=master
   :target: https://requires.io/github/alecxe/scrapy-beautifulsoup/requirements/?branch=master


