from datetime import datetime
from pymongo import MongoClient

_CREATED_AT = "created_at"
_TEXT = "text"

"""A (somewhat) generic store for tweets which can be queried by
key words and time ranges, and filled with a list of tweets."""
class TweetStore:

    # TODO: Add indices on created_at (and maybe text?)

    """Initializes this instance with the specified database name."""
    def __init__(self, dbname):
        self._dbname = dbname

        self._client = MongoClient()
        self._collection = self._client[dbname].test_collection

    """Retrieves a list of tweets in twython's format from the database.
    Tweets are filtered by the specified keywords and time range.
    keywords is a list of strings.
    start and end are datetime objects."""
    def get(self, keywords, start, end):
        c = self._collection
        return c.find(
                { _TEXT: {"$regex": "^.*(" + "|".join(keywords) + ").*$"}
                , _CREATED_AT:
                    { "$gte": start
                    , "$lte": end
                    }
                })

    """Twython gives us date fields as strings. This function converts date fields we care
    about (such as "created_at") into proper datetime objects."""
    def _str_to_date(self, tweet):
        if type(tweet[_CREATED_AT]) is datetime:
            return tweet
        # strptime does not always accept %z for the timezone in 2.7, so we have
        # to handle it manually. The initial format is: Sun Oct 20 19:48:26 +0000 2013
        datestr = tweet[_CREATED_AT]
        dt = datetime.strptime(datestr[0:20] + datestr[26:], "%a %b %d %H:%M:%S %Y")
        tweet[_CREATED_AT] = dt
        return tweet

    """Stores the specified tweets into the database."""
    def put(self, tweets):
        dateified_tweets = map(self._str_to_date, tweets)
        self._collection.insert(dateified_tweets)

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
        print t[_TEXT]
        print t[_CREATED_AT]
