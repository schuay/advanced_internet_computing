#!/bin/python2

import getopt
import json
import signal
import sys
import thread
import threading
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

manager = None

def signal_handler(signal, frame):
    if manager is not None:
        manager.stop()

class MyStreamer(TwythonStreamer):
    """In addition to initializing the TwythonStreamer class, sets our tweet store
       so we can persist retrieved tweets."""
    def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, store, parent, search_to):
        super(MyStreamer, self).__init__(app_key, app_secret, oauth_token, oauth_token_secret)
        self._buffer = []
        self.parent = parent
        self._store = store
        self.search_to = search_to

    def on_success(self, data):
        self._buffer.append(data)
        self.parent.updateStreamProgress()

        if len(self._buffer) > CHUNK_SIZE:
            self.flush()

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()

    def check_tweets(self, tweets):
        map(tweet.to_date, tweets)
        t = [t for t in tweets if t[tweet.CREATED_AT] <= self.search_to]
        if len(t) > 0:
            self._store.put(t)
        else:
            self.disconnect()

    def flush(self):
        self.check_tweets(self._buffer)
        del self._buffer[:]

class StreamThread(threading.Thread):
    def __init__(self, credentials, search_kw, search_to, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.credentials = credentials
        self.search_kw = search_kw
        self.search_to = search_to
        self.stream = None
    def exit(self):
        if self.stream is not None:
            self.stream.flush()
            self.stream.disconnect()
    def run(self):
        try:
            store = TweetStore("tweets")
            self.stream = MyStreamer(self.credentials['APP_KEY'],
                                self.credentials['APP_SECRET'],
                                self.credentials['TOKEN_KEY'],
                                self.credentials['TOKEN_SECRET'],
                                store,
                                self.parent,
                                search_to)
            self.stream.statuses.filter(locations = WORLD,
                                   language = 'en',
                                   track = self.search_kw)
        finally:
            store.close()

class SearchThread(threading.Thread):
    def __init__(self, credentials, search_kw, search_from, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.credentials = credentials # TODO: private vars with _ prefix
        self.search_kw = search_kw
        self.search_from = search_from
        self.loop = True

    def exit(self):
        self.loop = False

    def run(self):
        store = TweetStore("tweets")
        count = sys.maxint
        twitter = Twython(self.credentials['APP_KEY'],
                            self.credentials['APP_SECRET'],
                            self.credentials['TOKEN_KEY'],
                            self.credentials['TOKEN_SECRET'])
        search_args = { "q": self.search_kw
                      , "until": datetime.now().strftime("%Y-%m-%d")
                      , "lang": 'en'
                      , "result_type": 'recent'
                      , "count": 100
                      }

        retrieved = 0 # TODO: Remove retrieved and count
        while self.loop:
            # https://dev.twitter.com/docs/api/1.1/get/search/tweets
            try:
                result = twitter.search(**search_args)
                tweets = result["statuses"]

                if len(tweets) == 0:
                    break

                for tweet in tweets:
                    # check date
                    tweet.to_date(tweet)
                    if self.search_from <= tweet[tweet.CREATED_AT]:
                        self.parent.updateSearchProgress()
                        store.put([tweet])      # TODO: Don't insert 1-by-1.
                    else:
                        retrieved = sys.maxint
                        break

                retrieved += len(tweets)
                if retrieved >= count:
                    break

                search_args["max_id"] = min(int(t["id"]) for t in tweets) - 1
            except TwythonRateLimitError:
                print "Rate limit reached, sleeping for %d seconds..." % TIMEOUT
                time.sleep(TIMEOUT)
            except TwythonError:
                break

        store.close() # TODO: finally: 

class Manager():
    def init(self, credentials, search_kw, search_from, search_to):
        self._search_tweets = 0
        self._stream_tweets = 0

        self._progressbar = ProgressBar(widgets = [ AnimatedMarker()
                                                  , ' '
                                                  , Timer()
                                                  , ', # of Tweets: '
                                                  , Counter()
                                                  ],
                                        maxval = UnknownLength)
        self._progressbar.start()

        self.stream_thread = StreamThread(credentials, search_kw, search_to, self)
        self.search_thread = SearchThread(credentials, search_kw, search_from, self)

        self.stream_thread.start()
        self.search_thread.start()

        while threading.activeCount() > 1:
            time.sleep(0.01)    # Python can't receive signals while blocked in thread.join()..

    def updateStreamProgress(self):
        self._stream_tweets += 1
        self.update()

    def updateSearchProgress(self):
        self._search_tweets += 1
        self.update()

    def update(self):
        self._progressbar.update((self._search_tweets + self._stream_tweets))

    def stop(self):
        self._progressbar.finish()
        if self.search_thread is not None:
            self.search_thread.exit()
        if self.stream_thread is not None:
            self.stream_thread.exit()

if __name__ == '__main__':
    search_from = datetime.utcnow()
    search_to = datetime.utcnow()
    search_kw = "The Beatles"

    opts, args = getopt.getopt(sys.argv[1:], "q:f:t:")
    for o, a in opts:
        if o == "-f":
            search_from = datetime.strptime(a, "%Y-%m-%d")
        elif o == "-t":
            search_to = datetime.strptime(a, "%Y-%m-%d")
        elif o == "-q":
            search_kw = a
        else:
            print("USAGE: %s [-q query] [-f from_date] [-t to_date]" % sys.argv[0])
            sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    with open(CREDENTIALS_FILE, 'r') as f:
        credentials = json.loads(f.read())

    manager = Manager()
    manager.init(credentials, search_kw, search_from, search_to) # TODO: Move args to ctor, run() method
