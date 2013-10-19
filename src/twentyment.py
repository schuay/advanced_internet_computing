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
# You will need both a 'Consumer key/Consumer secret' and an 'Access token/Access
# token secret' for this example to work. Check the docs for info on how to get this.

from twython import Twython
from twython import TwythonStreamer

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()

if __name__ == '__main__':
    stream = MyStreamer(APP_KEY, APP_SECRET,
                    TOKEN_KEY, TOKEN_SECRET)
    stream.statuses.filter(locations = '-180,-90,180,90')
