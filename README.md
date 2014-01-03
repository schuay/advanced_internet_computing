Twitter Sentiment Analysis
==========================

This project is part of the Advanced Internet Computing course at
the Vienna University of Technology (TU Wien) in the winter semester 2013.

Installation
------------

Install all required dependencies:

* python2
* python2-flask
* python2-oauthlib: https://github.com/idan/oauthlib
* python2-progressbar
* python2-pymongo
* python2-requests-oauthlib: https://github.com/requests/requests-oauthlib
* python2-requests: http://docs.python-requests.org/en/latest/
* python2-scikit-learn
* python2-twython: https://github.com/ryanmcgrath/twython

In case you run into errors in requests/requests-oauthlib, try the quick fix in
https://github.com/requests/requests-oauthlib/pull/43#issuecomment-18158871.

Usage
-----

This project uses the twitter API, and as such some scripts require login
credentials.  These can be generated using the 'getsillytokens.py' script by
using the application key and application secret (you do have those, right?).
