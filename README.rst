====
News
====

|build| |coverage|

|logo|

.. |build| image:: https://travis-ci.org/kuc2477/news.svg?branch=dev
    :target: https://travis-ci.org/kuc2477/news

.. |coverage| image:: https://coveralls.io/repos/github/kuc2477/news/badge.svg?branch=dev
    :target: https://coveralls.io/github/kuc2477/news?branch=dev

.. |logo| image:: http://emojipedia-us.s3.amazonaws.com/cache/31/52/3152d71c04eb9dc2082c057e466b35cb.png
    :alt: News, subscription engine built on top of asynchronosy

News is an asynchronous web subscription engine built on top of :mod:`asnycio` and :mod:`aiohttp`. ::


Author
======
* `Ha Junsoo <kuc2477@gmail.com>`_


Requirements
============
* Python 3.5+
* Redis (optional)


Documentation
=============
* `Read the Docs <http://news.readthedocs.org/en/latest>`_


Note
====
- The project is currently under heavy development. Most of public APIs are settled but it can break your
  system at any time due to it's breaking change. Make sure to check release notes before you
  add ``news`` to your dependencies.
- You can check the roadmap at ``ROADMAP.org``
