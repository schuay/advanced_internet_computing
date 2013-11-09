#!/bin/python2

import getopt
import json
import signal
import sys

from datetime import datetime
from twython import Twython

CREDENTIALS_FILE = 'credentials.txt'

if __name__ == '__main__':
    count = sys.maxint
    search_args = { "q": "The Beatles"
                  , "until": datetime.now().strftime("%Y-%m-%d")
                  , "lang": 'en'
                  , "result_type": 'recent'
                  , "count": 100
                  }

    opts, args = getopt.getopt(sys.argv[1:], "hc:q:u:")
    for o, a in opts:
        if o == "-c":
            count = int(a)
        elif o == "-q":
            search_args["q"] = a
        elif o == "-u":
            search_args["until"] = a
        else:
            print "You're on your own..."
            sys.exit(0)

    with open(CREDENTIALS_FILE, 'r') as f:
        credentials = json.loads(f.read())

    twitter = Twython(
        credentials['APP_KEY'],
        credentials['APP_SECRET'],
        credentials['TOKEN_KEY'],
        credentials['TOKEN_SECRET'])

    retrieved = 0
    while True:
        # https://dev.twitter.com/docs/api/1.1/get/search/tweets
        result = twitter.search(**search_args)
        tweets = result["statuses"]

        if len(tweets) == 0:
            break

        for tweet in tweets:
            print tweet["created_at"][0:10], tweet["text"]

        retrieved += len(tweets)
        if retrieved >= count:
            break

        search_args["max_id"] = min(int(t["id"]) for t in tweets) - 1

    print "Retrieved %d tweets" % retrieved
