#!/bin/python2

import tweet

from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

"""A (somewhat) generic store for tweets which can be queried by
key words and time ranges, and filled with a list of tweets."""
class TweetStore:

    """Initializes this instance with the specified database name."""
    def __init__(self, dbname):
        self._dbname = dbname

        self._client = MongoClient()
        self._collection = self._client[dbname].test_collection

        self._collection.ensure_index(tweet.CREATED_AT)
        self._collection.ensure_index(tweet.ID, unique = True, drop_dups = True)
        self._collection.ensure_index(tweet.TEXT, unique = True, drop_dups = True)

    """Retrieves a list of tweets in twython's format from the database.
    Tweets are filtered by the specified keywords and time range.
    keywords is a list of strings.
    start and end are datetime objects."""
    def get(self, keywords, start, end):
        c = self._collection
        cursor = c.find(
                { tweet.TEXT: {"$regex": "^.*(" + "|".join(keywords) + ").*$", "$options": "-i"}
                , tweet.CREATED_AT:
                    { "$gte": start
                    , "$lte": end
                    }
                })
        # FIXME: Use twitter's include_retweets parameter instead of this filter and the
        # unique TEXT index.
        tweets = filter(lambda t: not t[tweet.TEXT].startswith("RT "), cursor)
        return tweets

    """Stores the specified tweets into the database."""
    def put(self, tweets):
        dateified_tweets = map(tweet.to_date, tweets)
        if len(dateified_tweets) == 0:
            return

        try:
            self._collection.insert(dateified_tweets, continue_on_error = True)
        except DuplicateKeyError:
            pass # Ignored.

# TODO: Rename module since it's not only about tweets.
# TODO: Add tweet_ prefix to get/put. Implement task fn's.

    """Retrieves a task by id, or returns None if not found."""
    def task_get(self, task_id):
        pass # TODO

    """Upserts the passed task."""
    def task_put(self, task):
        pass # TODO

    """Performs final cleanups such as closing the DB connection."""
    def close(self):
        self._client.close()

import getopt
import sys

def usage():
    print("USAGE: %s [-d database] [-k keyword] [-s 2013-01-31] [-e 2013-03-22]" %
            sys.argv[0])

if __name__ == "__main__":
    db = "tweets"
    keywords = []
    start = datetime(2013, 1, 1)
    end = datetime(2999, 1, 1)

    opts, args = getopt.getopt(sys.argv[1:], "hd:k:s:e:")
    for o, a in opts:
        if o == "-d":
            db = a
        elif o == "-k":
            keywords.append(a)
        elif o == "-s":
            start = datetime.strptime(a, "%Y-%M-%d")
        elif o == "-e":
            end = datetime.strptime(a, "%Y-%M-%d")
        else:
            usage()
            sys.exit(0)

    ts = TweetStore(db)
    for t in ts.get(keywords, start, end):
        print t[tweet.TEXT]
        print t[tweet.CREATED_AT]
