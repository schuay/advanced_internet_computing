#!/usr/bin/env python2

import task
import tweet

from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

TWEET_COLLECTION = "test_collection"
TASK_COLLECTION  = "task_tweet_coll"

"""A (somewhat) generic store for tweets which can be queried by
key words and time ranges, and filled with a list of tweets."""
class TweetStore:

    """Initializes this instance with the specified database name."""
    def __init__(self, dbname):
        self._dbname = dbname

        self._client = MongoClient()

        self._tweet_coll = self._client[dbname][TWEET_COLLECTION]
        self._tweet_coll.ensure_index(tweet.CREATED_AT)
        self._tweet_coll.ensure_index(tweet.ID, unique = True, drop_dups = True)
        self._tweet_coll.ensure_index(tweet.TEXT, unique = True, drop_dups = True)

        self._task_coll = self._client[dbname][TASK_COLLECTION]
        self._task_coll.ensure_index(task.ID, unique = True, drop_dups = True)

    """Retrieves a list of tweets in twython's format from the database.
    Tweets are filtered by the specified keywords and time range.
    keywords is a list of strings.
    start and end are datetime objects."""
    def get(self, keywords, start, end):
        c = self._tweet_coll
        cursor = c.find(
                { tweet.TEXT: {"$regex": "^.*(" + "|".join(keywords) + ").*$", "$options": "-i"}
                , tweet.CREATED_AT:
                    { "$gte": start
                    , "$lte": end
                    }
                })
        # Filter retweets. This is here, so that we can use old databases without having to worry
        # about them containing retweets. We actually filter them on insert too.
        tweets = filter(lambda t: not tweet.RETWEETED_STATUS in t, cursor)
        return tweets

    """Stores the specified tweets into the database."""
    def put(self, tweets):
        filtered_tweets = filter(lambda t: not tweet.RETWEETED_STATUS in t, tweets)
        normalized_tweets = map(lambda t: tweet.to_date(tweet.to_ascii(t)), filtered_tweets)

        if len(normalized_tweets) == 0:
            return

        try:
            self._tweet_coll.insert(normalized_tweets, continue_on_error = True)
        except DuplicateKeyError:
            pass # Ignored.

# TODO: Rename module since it's not only about tweets.
# TODO: Add tweet_ prefix to get/put.

    """Retrieves a list of all tasks."""
    def task_get_all(self):
        ts = list(self._task_coll.find());
        for t in ts:
            t.pop('_id')
        return ts

    """Retrieves a task by id, or returns None if not found."""
    def task_get(self, task_id):
        t = self._task_coll.find_one({ task.ID: task_id });
        if t is not None:
            t.pop('_id')
        return t

    """Deletes a task by id if it exists."""
    def task_rm(self, task_id):
        self._task_coll.remove({ task.ID: task_id });

    """Upserts the passed task."""
    def task_put(self, t):
        self._task_coll.update({task.ID: t[task.ID]},
                               {"$set": t},
                               upsert = True)

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
        try:
            print t[tweet.TEXT]
            print t[tweet.CREATED_AT]
        except:
            pass # FIXME: dirty hack to work around some encoding issues
