#!/bin/python2
# Imports the tweet database as provided by AIC into our data store.

from datetime import datetime
from itertools import islice
from progressbar import ProgressBar, AnimatedMarker, Timer, Counter, UnknownLength
from pymongo import MongoClient
from tweetstore import TweetStore

import getopt
import json
import sys

CHUNK_SIZE = 1024

def usage():
    print("USAGE: %s [-f file] [-d database]" % sys.argv[0])
    sys.exit(1)

if __name__ == "__main__":
    db = "tweets"
    filename = None

    opts, args = getopt.getopt(sys.argv[1:], "hd:f:")
    for o, a in opts:
        if o == "-d":
            db = a
        elif o == "-f":
            filename = a
        else:
            usage()

    if filename is None:
        usage()

    count = 0
    buf = []
    progressbar = ProgressBar(widgets = [ AnimatedMarker()
                                        , ' '
                                        , Timer()
                                        , ', # of Tweets: '
                                        , Counter()
                                        ],
                              maxval = UnknownLength)
    progressbar.start()

    ts = TweetStore(db)
    with open(filename) as f:
        for line in islice(f, 1, None, 2):
            buf.append(json.loads(line))
            if len(buf) > CHUNK_SIZE:
                ts.put(buf)
                del buf[:]

            count += 1
            progressbar.update(count)
