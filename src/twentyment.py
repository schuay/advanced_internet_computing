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

import getopt
import json
import signal
import sys

from pymongo import MongoClient
from twython import Twython
from twython import TwythonStreamer

CHUNK_SIZE = 1024
CREDENTIALS_FILE = 'credentials.txt'
WORLD = '-180,-90,180,90'

stream = None
verbose = False

def signal_handler(signal, frame):
    if stream is not None:
        print("Goodbye!")
        stream.disconnect()

class MyStreamer(TwythonStreamer):
    """In addition to initializing the TwythonStreamer class, sets our MongoDB collection
       so we can persist retrieved tweets."""
    def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, collection):
        super(MyStreamer, self).__init__(app_key, app_secret, oauth_token, oauth_token_secret)
        self._collection = collection
        self._buffer = []

    def on_success(self, data):
        self._buffer.append(data)
        if verbose and 'text' in data:
            print data['text'].encode('utf-8')

        if len(self._buffer) > CHUNK_SIZE:
            self._collection.insert(self._buffer)
            del self._buffer[:]

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "v")
    for o, a in opts:
        if o == "-v":
            verbose = True

    signal.signal(signal.SIGINT, signal_handler)

    with open(CREDENTIALS_FILE, 'r') as f:
        credentials = json.loads(f.read())

    try:
        client = MongoClient()
        collection = client.test_database.test_collection

        stream = MyStreamer(credentials['APP_KEY'],
                            credentials['APP_SECRET'],
                            credentials['TOKEN_KEY'],
                            credentials['TOKEN_SECRET'],
                            collection)
        stream.statuses.filter(locations = WORLD,
                               language = 'en')
    finally:
        client.close()
