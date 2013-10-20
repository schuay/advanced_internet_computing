#!/bin/python2

# This example uses python2-twython: https://github.com/ryanmcgrath/twython
#
# Twython depends on
# python2-requests-oauthlib: https://github.com/requests/requests-oauthlib
# python2-requests: http://docs.python-requests.org/en/latest/
# python2-oauthlib: https://github.com/idan/oauthlib
#
# On my machine I ran into this bug, which I 'fixed' using
# https://github.com/requests/requests-oauthlib/pull/43#issuecomment-18158871
# If you are able to fix this properly, let me know.
#
# MongoDB support requires python2-pymongo.
#
# You will need both a 'Consumer key/Consumer secret' and an 'Access token/Access
# token secret' for this example to work. Check the docs for info on how to get this.
# Store these in a file called 'credentials.txt'. An example file is as follows:
#
# {"APP_SECRET": "the_app_secret",
#  "TOKEN_KEY": "the_token_key",
#  "APP_KEY": "the_app_key",
#  "TOKEN_SECRET": "the_token_secret"}

import json

from pymongo import MongoClient
from twython import Twython
from twython import TwythonStreamer

collection = None

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        collection.insert(data)
        if 'text' in data:
            print data['text'].encode('utf-8')

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()

if __name__ == '__main__':
    credentials = None
    with open('credentials.txt', 'r') as f:
        credentials = json.loads(f.read())

    client = MongoClient()
    db = client.test_database
    collection = db.test_collection

    stream = MyStreamer(credentials['APP_KEY'],
                        credentials['APP_SECRET'],
                        credentials['TOKEN_KEY'],
                        credentials['TOKEN_SECRET'])
    stream.statuses.filter(locations = '-180,-90,180,90')
