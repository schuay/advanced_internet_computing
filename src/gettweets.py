#!/bin/python2

import getopt
import json
import signal
import sys
import time
import tweet

from datetime import datetime, timedelta
from progressbar import ProgressBar, AnimatedMarker, Timer, Counter, UnknownLength
from tweetstore import TweetStore
from twython import Twython
from twython import TwythonStreamer
from twython import TwythonRateLimitError, TwythonError

CHUNK_SIZE = 1024
CREDENTIALS_FILE = 'credentials.txt'
WORLD = '-180,-90,180,90'
TIMEOUT = 900

fetcher = None

def signal_handler(signal, frame):
    if fetcher is not None:
        fetcher.stop()

class MyStreamer(TwythonStreamer):
    """In addition to initializing the TwythonStreamer class, sets our tweet store
       so we can persist retrieved tweets."""
    def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, store, parent, search_to):
        super(MyStreamer, self).__init__(app_key, app_secret, oauth_token, oauth_token_secret)
        self._buffer = []
        self._parent = parent
        self._store = store
        self._search_to = search_to

    def on_success(self, data):
        t = tweet.to_date(data)

        if t[tweet.CREATED_AT] > self._search_to:
            self.flush()
            self.disconnect()
            return

        self._buffer.append(t)
        self._parent.update()

        if len(self._buffer) > CHUNK_SIZE:
            self.flush()

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()

    def flush(self):
        self._store.put(self._buffer)
        del self._buffer[:]

class TweetFetcher():
    def __init__(self, credentials, search_kw, search_from, search_to):
        self._credentials = credentials
        self._loop = True
        self._retrieved = 0
        self._search_from = search_from
        self._search_kw = search_kw
        self._search_to = search_to
        self._store = None
        self._stream = None

        self._progressbar = ProgressBar(widgets = [ AnimatedMarker()
                                                  , ' '
                                                  , Timer()
                                                  , ', # of Tweets: '
                                                  , Counter()
                                                  ],
                                        maxval = UnknownLength)
        self._progressbar.start()

    def run(self):
        try:
            self._store = TweetStore("tweets")
            self._fetch_tweets()

            if not self._loop:
                return

            self._fetch_stream_tweets()
        finally:
            if self._store is not None:
                self._store.close()
            self._progressbar.finish()

    def _fetch_tweets(self):
        twitter = Twython(self._credentials['APP_KEY'],
                            self._credentials['APP_SECRET'],
                            self._credentials['TOKEN_KEY'],
                            self._credentials['TOKEN_SECRET'])
        search_args = { "q": self._search_kw
                      , "until": datetime.now().strftime("%Y-%m-%d")
                      , "lang": 'en'
                      , "result_type": 'recent'
                      , "count": 100
                      }

        while self._loop:
            # https://dev.twitter.com/docs/api/1.1/get/search/tweets
            try:
                result = twitter.search(**search_args)
                tweets = result["statuses"]

                # Filter by date.
                tweets = map(tweet.to_date, tweets)
                tweets = [t for t in tweets if self._search_from <= t[tweet.CREATED_AT]]

                if len(tweets) == 0:
                    break

                self._store.put(tweets)
                self.update(len(tweets))

                search_args["max_id"] = min(int(t["id"]) for t in tweets) - 1
            except TwythonRateLimitError:
                print "Rate limit reached, sleeping for %d seconds..." % TIMEOUT
                time.sleep(TIMEOUT)
            except TwythonError:
                break

    def _fetch_stream_tweets(self):
        self._stream = MyStreamer(self._credentials['APP_KEY'],
                            self._credentials['APP_SECRET'],
                            self._credentials['TOKEN_KEY'],
                            self._credentials['TOKEN_SECRET'],
                            self._store,
                            self,
                            self._search_to)
        self._stream.statuses.filter(language = 'en',
                                     track = self._search_kw)

    def update(self, count = 1):
        self._retrieved += count
        self._progressbar.update(self._retrieved)

    def stop(self):
        self._loop = False
        if self._stream is not None:
            self._stream.flush()
            self._stream.disconnect()

if __name__ == '__main__':
    search_from = datetime.utcnow()
    search_to = datetime.utcnow() + timedelta(days = 1)
    search_kw = "The Beatles" # TODO: Allow multiple keywords

    opts, args = getopt.getopt(sys.argv[1:], "k:s:e:h")
    for o, a in opts:
        if o == "-s":
            search_from = datetime.strptime(a, "%Y-%m-%d")
        elif o == "-e":
            search_to = datetime.strptime(a, "%Y-%m-%d")
        elif o == "-k":
            search_kw = a
        else:
            print("USAGE: %s [-k keywords] [-s from_date] [-e to_date]" % sys.argv[0])
            sys.exit(1)

    print "Retrieving matches for '%s' from %s to %s" % (search_kw, str(search_from), str(search_to))

    signal.signal(signal.SIGINT, signal_handler)

    with open(CREDENTIALS_FILE, 'r') as f:
        credentials = json.loads(f.read())

    fetcher = TweetFetcher(credentials, search_kw, search_from, search_to)
    fetcher.run()
